from django.contrib import admin
from .models import Team, Round, Problem, Submission, RoundParticipation

class ProblemInline(admin.StackedInline):
    model = Problem
    extra = 1

class RoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'duration_minutes', 'is_active')
    inlines = [ProblemInline]

class RoundParticipationAdmin(admin.ModelAdmin):
    list_display = ('team', 'round', 'language', 'start_time', 'is_malpractice', 'is_completed')
    list_filter = ('round', 'language', 'is_malpractice')

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('team', 'problem', 'score', 'time_taken_seconds')
    list_filter = ('problem',)

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'member1_name', 'member2_name')

admin.site.register(Team, TeamAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Problem)
admin.site.register(RoundParticipation, RoundParticipationAdmin)
admin.site.register(Submission, SubmissionAdmin)
