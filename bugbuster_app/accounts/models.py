from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('coordinator', 'Coordinator'),
        ('participant', 'Participant'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='participant')

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_coordinator(self):
        return self.role == 'coordinator'

    @property
    def is_participant(self):
        return self.role == 'participant'

    def __str__(self):
        return f"{self.username} ({self.role})"
