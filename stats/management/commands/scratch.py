from django.core.management.base import BaseCommand, CommandError
from stats.strava import Athlete,Strava


class Command(BaseCommand):
    def handle(self, *args, **options):
        a = Athlete()
        print(a.get_athlete_stats())

        s = Strava()
        print(s.get_organized_activities())
