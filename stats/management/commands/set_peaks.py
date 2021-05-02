from django.core.management.base import BaseCommand
from stats.strava import Strava


class Command(BaseCommand):
    help = 'Sets the peak for the current year'

    def handle(self, *args, **options):
        s = Strava()
        s.get_yearly_peaks()
