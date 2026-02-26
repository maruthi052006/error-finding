from django.db import models
from django.conf import settings

class Team(models.Model):
    name = models.CharField(max_length=100, unique=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='team')
    member1_name = models.CharField(max_length=100)
    member1_email = models.EmailField()
    member1_roll = models.CharField(max_length=50)
    member2_name = models.CharField(max_length=100, blank=True, null=True)
    member2_email = models.EmailField(blank=True, null=True)
    member2_roll = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name

class Round(models.Model):
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Hard', 'Hard'),
    ]
    name = models.CharField(max_length=50)
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES)
    duration_minutes = models.IntegerField(default=15)
    is_active = models.BooleanField(default=False)
    start_time = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} ({self.difficulty})"

class Problem(models.Model):
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='problems')
    title = models.CharField(max_length=200)
    description = models.TextField()
    buggy_code_c = models.TextField(blank=True, null=True)
    buggy_code_python = models.TextField(blank=True, null=True)
    expected_output = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.title

class RoundParticipation(models.Model):
    LANGUAGE_CHOICES = [
        ('C', 'C'),
        ('Python', 'Python'),
    ]
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='participations')
    round = models.ForeignKey(Round, on_delete=models.CASCADE, related_name='participations')
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES)
    start_time = models.DateTimeField(auto_now_add=True)
    is_malpractice = models.BooleanField(default=False)
    is_completed = models.BooleanField(default=False)
    assigned_problems = models.ManyToManyField(Problem, blank=True)
    
    class Meta:
        unique_together = ('team', 'round')

    def __str__(self):
        return f"{self.team.name} - {self.round.name} Participation"

class Submission(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='submissions')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name='submissions')
    submitted_code = models.TextField(blank=True, null=True)
    time_taken_seconds = models.IntegerField(default=0)
    tab_switches = models.IntegerField(default=0)
    score = models.IntegerField(default=0) # This will be the total sum
    score_time = models.IntegerField(default=0)
    score_errors = models.IntegerField(default=0)
    score_logic = models.IntegerField(default=0)
    score_structure = models.IntegerField(default=0)
    score_tabs = models.IntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('team', 'problem')

    def __str__(self):
        return f"{self.team.name} - {self.problem.title}"
