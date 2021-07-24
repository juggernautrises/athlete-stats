import datetime
import time
from django.db import models


class Mood(models.Model):
    number = models.IntegerField()
    mood_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True, blank=True)

    class Meta:
        ordering = ('mood_date',)

    def __str__(self):
        day = self.mood_date.day
        month = self.mood_date.month
        return f'{self.id}: {month}/{day}: {self.number}'


class Peaks(models.Model):
    longest_run = models.FloatField(default=0.0)
    longest_ride = models.FloatField(default=0.0)
    longest_run_date = models.DateTimeField(
        default=datetime.datetime.utcnow)
    longest_ride_date = models.DateTimeField(
        default=datetime.datetime.utcnow)


class StravaToken(models.Model):
    access_token = models.CharField(max_length=255)
    expires_at = models.FloatField()

    @property
    def is_expired(self):
        return self.expires_at < time.time()
