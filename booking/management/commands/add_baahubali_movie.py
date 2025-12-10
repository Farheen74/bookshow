from django.core.management.base import BaseCommand
from staff.models import film, banner

class Command(BaseCommand):
    help = 'Add Baahubali movie with banner image'

    def handle(self, *args, **options):
        # Check if Baahubali already exists
        try:
            movie = film.objects.get(movie_name='Baahubali')
            self.stdout.write(self.style.WARNING(f'Baahubali movie already exists'))
            return
        except film.DoesNotExist:
            pass

        # Create Baahubali film
        movie = film.objects.create(
            movie_name='Baahubali',
            movie_genre='Action, Adventure, Fantasy',
            movie_lang='Telugu',
            movie_year=2015,
            movie_plot='When Shiva learns about his ancestry and lineage, he travels back in time to stop a politically motivated villain.',
            url='https://images.moviesanywhere.com/bdc0c5e86b5aca3cf3f5e22dd0fc7f7d.jpg'
        )

        # Create banner for Baahubali
        banner.objects.create(
            movie=movie,
            url='https://images.moviesanywhere.com/bdc0c5e86b5aca3cf3f5e22dd0fc7f7d.jpg'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created Baahubali movie!\n'
                f'Movie: {movie.movie_name}\n'
                f'Genre: {movie.movie_genre}\n'
                f'Language: {movie.movie_lang}\n'
                f'Year: {movie.movie_year}'
            )
        )
