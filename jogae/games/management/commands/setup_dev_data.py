from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'A master command to seed the database and then pre-compute the TF-IDF matrix.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('--- Starting Complete Development Setup ---'))

        self.stdout.write(self.style.NOTICE('\nStep 1: Seeding database with initial data...'))
        call_command('seed_data')
        self.stdout.write(self.style.SUCCESS('Database seeding complete.'))

        self.stdout.write(self.style.NOTICE('\nStep 2: Pre-computing TF-IDF matrix for recommendations...'))
        call_command('precompute_tfidf')
        self.stdout.write(self.style.SUCCESS('TF-IDF pre-computation complete.'))

        self.stdout.write(self.style.SUCCESS('\n--- Development data setup finished successfully! ---'))