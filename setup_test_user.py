import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bugbuster_app.settings')
django.setup()

from accounts.models import CustomUser
from events.models import Team

t, _ = Team.objects.get_or_create(name='testteam')
try:
    u = CustomUser.objects.get(username='testteam')
    u.set_password('password')
    u.team = t
    u.save()
except CustomUser.DoesNotExist:
    u = CustomUser.objects.create_user(username='testteam', email='testteam@example.com', password='password', role='participant')
    u.team = t
    u.save()
print('User testteam created')
