from django.contrib import admin
from .models import Team, Round, Problem, Submission

class ProblemInline(admin.StackedInline):
    model = Problem
    extra = 1

class RoundAdmin(admin.ModelAdmin):
    list_display = ('name', 'difficulty', 'duration_minutes', 'is_active')
    inlines = [ProblemInline]

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('team', 'round', 'language', 'score', 'time_taken_seconds', 'is_malpractice')
    list_filter = ('round', 'language', 'is_malpractice')

class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'member1_name', 'member2_name')

admin.site.register(Team, TeamAdmin)
admin.site.register(Round, RoundAdmin)
admin.site.register(Problem)
admin.site.register(Submission, SubmissionAdmin)
