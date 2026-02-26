from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Round, Problem, Team, Submission, RoundParticipation
from django.utils import timezone

def is_coordinator(user):
    return user.is_authenticated and (user.is_coordinator or user.is_admin)

@login_required
@user_passes_test(is_coordinator)
def coordinator_dashboard(request):
    rounds = Round.objects.all().order_by('-start_time')
    problems = Problem.objects.all()
    teams = Team.objects.all()
    
    if request.method == 'POST':
        if 'toggle_round' in request.POST:
            round_id = request.POST.get('round_id')
            r = Round.objects.get(id=round_id)
            r.is_active = not r.is_active
            if r.is_active and not r.start_time:
                r.start_time = timezone.now()
            r.save()
            return redirect('coordinator_dashboard')
            
        elif 'create_round' in request.POST:
            name = request.POST.get('name')
            difficulty = request.POST.get('difficulty')
            duration = request.POST.get('duration_minutes', 15)
            Round.objects.create(name=name, difficulty=difficulty, duration_minutes=duration)
            return redirect('coordinator_dashboard')
            
    context = {
        'rounds': rounds,
        'problems': problems,
        'teams_count': teams.count(),
    }
    return render(request, 'events/coordinator_dashboard.html', context)

@login_required
@user_passes_test(is_coordinator)
def upload_problem(request):
    if request.method == 'POST':
        round_id = request.POST.get('round_id')
        title = request.POST.get('title')
        description = request.POST.get('description')
        buggy_c = request.POST.get('buggy_c')
        buggy_python = request.POST.get('buggy_python')
        
        round_inst = Round.objects.get(id=round_id)
        Problem.objects.create(
            round=round_inst,
            title=title,
            description=description,
            buggy_code_c=buggy_c,
            buggy_code_python=buggy_python
        )
        return redirect('coordinator_dashboard')
    
    rounds = Round.objects.all()
    return render(request, 'events/upload_problem.html', {'rounds': rounds})

from django.db.models import Sum

import csv
from django.http import HttpResponse

@login_required
@user_passes_test(is_coordinator)
def analytics_view(request):
    teams = Team.objects.all()
    
    analytics_data = []
    labels = []
    scores = []
    times = []
    
    for team in teams:
        subs = Submission.objects.filter(team=team)
        if not subs.exists():
            continue
            
        total_time = subs.aggregate(Sum('time_taken_seconds'))['time_taken_seconds__sum'] or 0
        total_switches = subs.aggregate(Sum('tab_switches'))['tab_switches__sum'] or 0
        
        # Rubric split-ups
        score_logic = subs.aggregate(Sum('score_logic'))['score_logic__sum'] or 0
        score_structure = subs.aggregate(Sum('score_structure'))['score_structure__sum'] or 0
        score_time_pts = subs.aggregate(Sum('score_time'))['score_time__sum'] or 0
        score_tabs = subs.aggregate(Sum('score_tabs'))['score_tabs__sum'] or 0
        score_errors = subs.aggregate(Sum('score_errors'))['score_errors__sum'] or 0
        
        # total score
        total_score = subs.aggregate(Sum('score'))['score__sum'] or 0
        
        # Malpractice check
        has_malpractice = RoundParticipation.objects.filter(team=team, is_malpractice=True).exists()
        rounds_attended = RoundParticipation.objects.filter(team=team).count()
        
        members = team.member1_name
        if team.member2_name:
            members += f", {team.member2_name}"
            
        analytics_data.append({
            'team': team.name,
            'members': members,
            'rounds_attended': rounds_attended,
            'score_logic': score_logic,
            'score_structure': score_structure,
            'score_time_pts': score_time_pts,
            'score_tabs': score_tabs,
            'score_errors': score_errors,
            'score': total_score,
            'time': total_time,
            'switches': total_switches,
            'malpractice': has_malpractice
        })
        
    # Sort by score descending, then time ascending
    analytics_data.sort(key=lambda x: (-x['score'], x['time']))
    
    # Export to Excel/CSV Feature
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="bugbuster_analytics.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Rank', 'Team', 'Members', 'Rounds Attended', 'Logic Pts', 'Structure Pts', 'Time Pts', 'Tabs Pts', 'Errors Pts', 'Total Combined Score', 'Total Time (s)', 'Total Tab Switches', 'Malpractice Detected'])
        
        for idx, row in enumerate(analytics_data, 1):
            writer.writerow([
                idx,
                row['team'],
                row['members'],
                row['rounds_attended'],
                row['score_logic'],
                row['score_structure'],
                row['score_time_pts'],
                row['score_tabs'],
                row['score_errors'],
                row['score'],
                row['time'],
                row['switches'],
                'Yes' if row['malpractice'] else 'No'
            ])
        return response

    import json
    for d in analytics_data:
        labels.append(d['team'])
        scores.append(d['score'])
        times.append(d['time'])
    
    context = {
        'analytics_data': analytics_data,
        'labels_json': json.dumps(labels),
        'scores_json': json.dumps(scores),
        'times_json': json.dumps(times),
    }
    return render(request, 'events/analytics.html', context)
