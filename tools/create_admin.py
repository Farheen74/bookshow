import os
import sys
import django

# Ensure project root is on sys.path so Django settings can be imported
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "movieticket.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = 'admin1'
password = 'admin1234'
email = 'admin1@example.com'

u = User.objects.filter(username=username).first()
if u:
    u.set_password(password)
    u.is_staff = True
    u.is_superuser = True
    u.email = email
    u.save()
    print('Updated user', username)
else:
    User.objects.create_superuser(username, email, password)
    print('Created superuser', username)
