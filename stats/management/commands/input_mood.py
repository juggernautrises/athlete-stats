import csv
import datetime
import os
from pathlib import Path
from django.core.management.base import BaseCommand
from stats.models import Mood


class Command(BaseCommand):
    help = 'For adding mood data from .csv to the db.'

    # def add_arguments(self, parser):
    #     parser.add_argument('input_data', nargs='+')

    def handle(self, *args, **options):
        data_dir = os.path.dirname(Path(__file__).resolve())  + '/data'
        files = os.listdir(data_dir)
        files = [f for f in files if f.endswith('.csv')]
        moods = []
        for f in files:
            csv_path = os.path.join(data_dir, f)
            with open(csv_path, 'r') as fin:
                mood_data = csv.reader(fin)
                for row in mood_data:
                    date = row[0]
                    number = row[1]
                    if date:
                        dt = datetime.datetime.strptime(date, '%m/%d')
                        dt = dt.replace(year=2021)
                        mood = Mood(number=number, mood_date=dt)
                        moods.append(mood)
        Mood.objects.bulk_create(moods)
