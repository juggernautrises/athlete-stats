import datetime
import time
from django.db import models


class StravaToken(models.Model):
    access_token = models.CharField(max_length=255)
    expires_at = models.FloatField()

    @property
    def is_expired(self):
        return self.expires_at < time.time()


class Peaks(models.Model):
    longest_run = models.FloatField(default=0.0)
    longest_ride = models.FloatField(default=0.0)
    longest_run_date = models.DateTimeField(
        default=datetime.datetime.utcnow)
    longest_ride_date = models.DateTimeField(
        default=datetime.datetime.utcnow)
