from .base import *
import athlete_stats.config.settings.local_settings as local_settings

DEBUG = True

ALLOWED_HOSTS = local_settings.ALLOWED_HOSTS
SECRET_KEY = local_settings.SECRET_KEY


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'db.sqlite3',
    },
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql_psycopg2',
#         'NAME': local_settings.DB_NAME,
#         'USER': local_settings.DB_USER,
#         'PASSWORD': local_settings.DB_PASS,
#         'HOST': local_settings.DB_HOST,
#         'PORT': local_settings.DB_PORT
#     }
# }


STRAVA_DEFAULT_ACCESS_TOKEN = local_settings.STRAVA_DEFAULT_ACCESS_TOKEN
STRAVA_REFRESH_TOKEN = local_settings.STRAVA_REFRESH_TOKEN
ACTIVITIES_URL = local_settings.ACTIVITIES_URL
ATHLETE_ID = local_settings.ATHLETE_ID
ATHLETE_STATS_URL = local_settings.ATHLETE_STATS_URL
ATHLETE_URL = local_settings.ATHLETE_URL
CLIENT_ID = local_settings.CLIENT_ID
CLIENT_SECRET = local_settings.CLIENT_SECRET
CODE = local_settings.CODE
OAUTH_TOKEN_URL = local_settings.OAUTH_TOKEN_URL
RIDE_GOAL = local_settings.RIDE_GOAL
RUN_GOAL = local_settings.RUN_GOAL
