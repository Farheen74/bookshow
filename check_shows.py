import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movieticket.settings')
django.setup()

from staff.models import show, film
from datetime import date

# Check if there are any shows in the database
total_shows = show.objects.count()
total_movies = film.objects.count()

print(f"✓ Total shows in database: {total_shows}")
print(f"✓ Total movies in database: {total_movies}")

if total_shows > 0:
    print("\n✓ Recent shows:")
    for s in show.objects.all().order_by('-id')[:10]:
        print(f"  - {s.movie.movie_name if s.movie else 'Unknown'} at {s.showtime} ({s.start_date} to {s.end_date})")
else:
    print("\n⚠️  No shows found!")
