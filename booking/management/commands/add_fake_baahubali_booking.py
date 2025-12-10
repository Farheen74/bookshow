from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import date, timedelta
from booking.models import UserBooking
from accounts.models import Account

class Command(BaseCommand):
    help = 'Add fake Baahubali booking with image'

    def handle(self, *args, **options):
        # Get or create a default user (using the first admin or creating one)
        try:
            user = Account.objects.filter(is_superuser=True).first()
            if not user:
                # Create a test user if no admin exists
                user = Account.objects.create_user(
                    username='testuser',
                    email='test@example.com',
                    password='testpass123'
                )
        except:
            user = Account.objects.first()

        # Check if booking already exists
        existing = UserBooking.objects.filter(movie_name='Baahubali').first()
        if existing:
            self.stdout.write(self.style.WARNING(f'Baahubali booking already exists: {existing.ticket_number}'))
            return

        # Create fake Baahubali booking
        tomorrow = date.today() + timedelta(days=1)
        
        booking = UserBooking.objects.create(
            user=user,
            movie_name='Baahubali',
            theatre_name='PVR Cinemas',
            seats='A1, A2, A3',
            show_date=tomorrow,
            show_time='07:30 PM',
            price=1050,
            booked_on=timezone.now()
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created Baahubali booking!\n'
                f'Ticket Number: {booking.ticket_number}\n'
                f'Theatre: {booking.theatre_name}\n'
                f'Seats: {booking.seats}\n'
                f'Date: {booking.show_date}\n'
                f'Price: ₹{booking.price}'
            )
        )
