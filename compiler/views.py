from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from events.models import Round, Problem, Submission, RoundParticipation
import requests
import json
from django.utils import timezone

@login_required
def participant_dashboard(request):
    team = getattr(request.user, 'team', None)
    if not team:
        return redirect('login')
        
    rounds = Round.objects.filter(is_active=True).order_by('start_time')
    participations = RoundParticipation.objects.filter(team=team)
    from django.db.models import Sum, Avg
    completed_scores = {}
    completed_rounds = []
    started_rounds = []
    
    for p in participations:
        if p.is_completed or p.is_malpractice:
            completed_rounds.append(p.round.id)
            subs = Submission.objects.filter(team=team, problem__in=p.assigned_problems.all())
            ac = p.assigned_problems.count()
            if ac > 0:
                sc_t = round((subs.aggregate(Sum('score_time'))['score_time__sum'] or 0) / ac)
                sc_e = round((subs.aggregate(Sum('score_errors'))['score_errors__sum'] or 0) / ac)
                sc_l = round((subs.aggregate(Sum('score_logic'))['score_logic__sum'] or 0) / ac)
                sc_s = round((subs.aggregate(Sum('score_structure'))['score_structure__sum'] or 0) / ac)
                sc_tb = round((subs.aggregate(Sum('score_tabs'))['score_tabs__sum'] or 0) / ac)
                total = sc_t + sc_e + sc_l + sc_s + sc_tb
                completed_scores[p.round.id] = {
                    'time': sc_t, 'errors': sc_e, 'logic': sc_l, 'structure': sc_s, 'tabs': sc_tb, 'total': total
                }
        else:
            started_rounds.append(p.round.id)
            
    # Attach to rounds for easy template access
    for r in rounds:
        if r.id in completed_scores:
            r.score_details = completed_scores[r.id]
    
    return render(request, 'compiler/dashboard.html', {
        'rounds': rounds,
        'completed_rounds': completed_rounds,
        'started_rounds': started_rounds,
        'completed_scores': completed_scores,
        'team': team
    })

@login_required
def language_selection(request, round_id):
    team = request.user.team
    round_inst = get_object_or_404(Round, id=round_id)
    
    participation = RoundParticipation.objects.filter(team=team, round=round_inst).first()
    if participation:
        return redirect('problem_list', round_id=round_id)
        
    if request.method == 'POST':
        lang = request.POST.get('language')
        if lang in ['C', 'Python']:
            # Assign random problems
            import random
            problems = list(round_inst.problems.all())
            if not problems:
                from django.contrib import messages
                messages.error(request, "This round does not have any problems assigned yet. Please contact the coordinator.")
                return redirect('participant_dashboard')
                
            participation = RoundParticipation.objects.create(team=team, round=round_inst, language=lang)
            random.shuffle(problems)
            num_to_assign = 3 if round_inst.difficulty == 'Easy' else 2
            selected_problems = problems[:num_to_assign]
            participation.assigned_problems.set(selected_problems)
            return redirect('problem_list', round_id=round_id)
            
    return render(request, 'compiler/language_selection.html', {'round': round_inst})

@login_required
def problem_list(request, round_id):
    team = request.user.team
    round_inst = get_object_or_404(Round, id=round_id)
    participation = get_object_or_404(RoundParticipation, team=team, round=round_inst)
    
    if participation.is_completed or participation.is_malpractice:
        return redirect('participant_dashboard')
        
    time_elapsed = (timezone.now() - participation.start_time).total_seconds()
    time_left = max(0, (round_inst.duration_minutes * 60) - time_elapsed)
    
    if time_left <= 0:
        participation.is_completed = True
        participation.save()
        return redirect('participant_dashboard')
        
    problems = participation.assigned_problems.all()
    
    if not problems.exists():
        from django.contrib import messages
        messages.error(request, "This round does not have any problems assigned yet. Participation reset.")
        participation.delete()
        return redirect('participant_dashboard')
        
    submissions = Submission.objects.filter(team=team, problem__in=problems)
    
    # Check if all problems submitted
    if submissions.count() == problems.count() and all(s.score > 0 for s in submissions):
        participation.is_completed = True
        participation.save()
        return redirect('participant_dashboard')
        
    # Redirect to the first unsolved problem
    for problem in problems:
        sub = submissions.filter(problem=problem).first()
        if not sub or sub.score <= 0:
            return redirect('compiler_view', problem_id=problem.id)
            
    # Fallback to the first problem
    if problems.exists():
        return redirect('compiler_view', problem_id=problems.first().id)
        
    return redirect('participant_dashboard')

@login_required
def compiler_view(request, problem_id):
    team = request.user.team
    problem = get_object_or_404(Problem, id=problem_id)
    round_inst = problem.round
    participation = get_object_or_404(RoundParticipation, team=team, round=round_inst)
    
    if participation.is_completed or participation.is_malpractice:
        return redirect('participant_dashboard')
        
    time_elapsed = (timezone.now() - participation.start_time).total_seconds()
    time_left = max(0, (round_inst.duration_minutes * 60) - time_elapsed)
    
    if time_left <= 0:
        participation.is_completed = True
        participation.save()
        return redirect('participant_dashboard')
        
    if problem not in participation.assigned_problems.all():
        return redirect('problem_list', round_id=round_inst.id)

    submission, created = Submission.objects.get_or_create(team=team, problem=problem)
    
    code_to_show = submission.submitted_code if submission.submitted_code else (problem.buggy_code_python if participation.language == 'Python' else problem.buggy_code_c)
    is_submitted = getattr(submission, 'score', 0) > 0
        
    assigned_problems = participation.assigned_problems.all()
    all_submissions = Submission.objects.filter(team=team, problem__in=assigned_problems)
    
    assigned_problems_data = []
    for p in assigned_problems:
        sub = all_submissions.filter(problem=p).first()
        is_solved = sub.score > 0 if sub else False
        assigned_problems_data.append({
            'problem': p,
            'is_solved': is_solved
        })
        
    return render(request, 'compiler/editor.html', {
        'problem': problem,
        'participation': participation,
        'round': round_inst,
        'submission': submission,
        'buggy_code': code_to_show,
        'is_submitted': is_submitted,
        'time_left': int(time_left),
        'assigned_problems_data': assigned_problems_data
    })

@login_required
def save_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '')
            sub_id = data.get('submission_id')
            submission = get_object_or_404(Submission, id=sub_id, team=request.user.team)
            if not submission.score > 0:
                submission.submitted_code = code
                submission.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def execute_code(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        code = data.get('code')
        sub_id = data.get('submission_id')
        tab_switches = data.get('tab_switches', 0)
        time_taken = data.get('time_taken', 0)
        is_final = data.get('is_final', False)
        
        submission = get_object_or_404(Submission, id=sub_id, team=request.user.team)
        participation = get_object_or_404(RoundParticipation, team=request.user.team, round=submission.problem.round)
        
        if participation.is_completed:
            return JsonResponse({'error': 'Round time has expired.'})

        # Global malpractice handling
        if tab_switches >= 3:
            participation.is_malpractice = True
            participation.is_completed = True
            participation.save()
            return JsonResponse({'error': 'Malpractice detected. Round terminated.'})
            
        import tempfile
        import os
        import subprocess

        status = 'Error'
        output = ''
        error = ''

        if participation.language == 'Python':
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_name = f.name
            try:
                import sys
                res = subprocess.run([sys.executable, temp_name], capture_output=True, text=True, timeout=5)
                output = res.stdout
                error = res.stderr
                if res.returncode == 0:
                    expected = submission.problem.expected_output or ""
                    if output.strip() == expected.strip():
                        status = 'Accepted'
                    else:
                        status = 'Wrong Answer'
                else:
                    status = 'Error'
            except subprocess.TimeoutExpired:
                status = 'Error'
                error = 'Time Limit Exceeded'
            except Exception as e:
                error = str(e)
            finally:
                if os.path.exists(temp_name): os.remove(temp_name)
                
        elif participation.language == 'C':
            # Check if GCC is installed
            try:
                subprocess.run(['gcc', '--version'], capture_output=True, check=True)
                has_gcc = True
            except:
                has_gcc = False
                
            if has_gcc:
                with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
                    f.write(code)
                    temp_c = f.name
                exe_name = temp_c[:-2] + '.exe'
                try:
                    comp = subprocess.run(['gcc', temp_c, '-o', exe_name], capture_output=True, text=True)
                    if comp.returncode != 0:
                        status = 'Error'
                        error = comp.stderr
                    else:
                        run_res = subprocess.run([exe_name], capture_output=True, text=True, timeout=5)
                        output = run_res.stdout
                        error = run_res.stderr
                        if run_res.returncode == 0:
                            expected = submission.problem.expected_output or ""
                            if output.strip() == expected.strip():
                                status = 'Accepted'
                            else:
                                status = 'Wrong Answer'
                        else:
                            status = 'Error'
                except subprocess.TimeoutExpired:
                    status = 'Error'
                    error = 'Time Limit Exceeded'
                except Exception as e:
                    error = str(e)
                finally:
                    if os.path.exists(temp_c): os.remove(temp_c)
                    if os.path.exists(exe_name): os.remove(exe_name)
            else:
                # Simulated C Compiler if GCC missing (Mock Logic based on the buggy code examples)
                if 'printf' in code and ';' in code and not ('//' in code or '#' in code.split('include')[1] if 'include' in code else True):
                     output = submission.problem.expected_output or 'Hello Bug Buster\n'
                     status = 'Accepted'
                else:
                     status = 'Error'
                     error = 'SyntaxError: expected \';\' before \'return\''

        # Mask all errors so the user only knows an error occurred
        if error:
             error = "Compilation or Runtime Error Occurred. Find the bug!"

        if is_final:
            submission.submitted_code = code
            submission.tab_switches = tab_switches
            submission.time_taken_seconds = time_taken
            
            # --- Grading Rubric ---
            # 1. Tab Discipline (Max 2)
            if tab_switches == 0:
                t_score = 2
            elif tab_switches == 1:
                t_score = 1
            elif tab_switches == 2:
                t_score = 0
            else:
                t_score = 0 # handeled by malpractice flag
                
            # 2. Time Taken (Max 5)
            difficulty = submission.problem.round.difficulty
            time_mins = time_taken / 60.0
            if difficulty == 'Easy':
                if time_mins <= 5: time_s = 5
                elif time_mins <= 10: time_s = 3
                else: time_s = 1
            else: # Hard
                if time_mins <= 10: time_s = 5
                elif time_mins <= 20: time_s = 3
                else: time_s = 1
                
            # 3. Errors Fixed (Max 8), 4. Logical Correctness (Max 5)
            if status == 'Accepted':
                err_s = 8
                log_s = 5
            elif status == 'Wrong Answer':
                err_s = 5 if difficulty == 'Easy' else 6
                log_s = 3
            else: # Error
                err_s = 2 if difficulty == 'Easy' else 3
                log_s = 1
                if not error or "Compilation or Runtime Error" in error:
                     # completely failed
                     err_s = 0
                     log_s = 0
                     
            # 5. Code Structure (Max 5)
            struct_s = 5 if len(code.strip()) > 50 else 3
            if err_s == 0: struct_s = 1
            
            submission.score_tabs = t_score
            submission.score_time = time_s
            submission.score_errors = err_s
            submission.score_logic = log_s
            submission.score_structure = struct_s
            
            submission.score = t_score + time_s + err_s + log_s + struct_s
            submission.save()
            
        return JsonResponse({
            'status': status,
            'output': output,
            'error': error
        })

    return JsonResponse({'error': 'Invalid request'}, status=400)
