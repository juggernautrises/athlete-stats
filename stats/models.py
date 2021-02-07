import time
from django.db import models


class StravaToken(models.Model):
    refresh_token = models.CharField(max_length=255)
    expires_at = models.FloatField()

    @property
    def is_expired(self):
        return self.expires_at < time.time()
