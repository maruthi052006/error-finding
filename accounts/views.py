from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import TeamRegistrationForm
from .models import CustomUser
from events.models import Team
from django.contrib.auth.decorators import login_required

def register_view(request):
    if request.method == 'POST':
        form = TeamRegistrationForm(request.POST)
        if form.is_valid():
            # Create user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.role = 'participant'
            user.save()
            
            # Create team
            Team.objects.create(
                user=user,
                name=form.cleaned_data['team_name'],
                member1_name=form.cleaned_data['member1_name'],
                member1_email=form.cleaned_data['member1_email'],
                member1_roll=form.cleaned_data['member1_roll'],
                member2_name=form.cleaned_data['member2_name'],
                member2_email=form.cleaned_data['member2_email'],
                member2_roll=form.cleaned_data['member2_roll']
            )
            
            # Authenticate and login
            login(request, user)
            return redirect('dashboard')
    else:
        form = TeamRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def dashboard_redirect(request):
    user = request.user
    if user.is_admin:
        return redirect('/admin/')
    elif user.is_coordinator:
        return redirect('coordinator_dashboard')
    else:
        return redirect('participant_dashboard')
