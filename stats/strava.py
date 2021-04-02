import datetime
import http
import requests

from django.conf import settings
from stats.constants import METERS_TO_FEET, METERS_TO_MILES
from stats.exceptions import StravaExternalException
from stats.models import Peaks, StravaToken
from stats.serializers import PeaksSerializer


class Activity:
    def __init__(self, name, distance, moving_time, elevation_gain,
                 activity_type, start_date=None):
        self.name = name
        self.distance = distance
        self.moving_time = moving_time
        self.elevation_gain = elevation_gain
        self.activity_type = activity_type
        self.start_date = start_date if start_date else datetime.datetime.now()

    def get_activity_date(self):
        return self.start_date.strftime("%Y-%m-%d")

    def to_dict(self):
        return_dict = self.__dict__
        if self.moving_time >= 60*59:
            return_dict['moving_time'] = str(datetime.timedelta(
                seconds=self.moving_time))
        else:
            dt = str(datetime.timedelta(seconds=self.moving_time))
            return_dict['moving_time'] = ':'.join(dt.split(':')[1:])
        return_dict['start_date'] = self.start_date.strftime("%Y-%m-%d")
        return_dict['elevation_gain'] = int(self.elevation_gain
                                            * METERS_TO_FEET)
        return_dict['distance'] = round(self.distance * METERS_TO_MILES, 2)
        return return_dict


class StravaBase:
    def __init__(self):
        # TODO: Fix Strava tokens
        self.peaks = Peaks.objects.first()
        self.strava_token = StravaToken.objects.first()

        if not self.peaks:
            self.peaks = Peaks()
            self.peaks.save()

        if not self.strava_token:
            self.strava_token = StravaToken(
                access_token=settings.STRAVA_DEFAULT_ACCESS_TOKEN,
                expires_at=1)
            self.strava_token.save()

        if self.strava_token.is_expired:

            response = requests.post(
                url=settings.OAUTH_TOKEN_URL,
                data={
                    'client_id': settings.CLIENT_ID,
                    'client_secret': settings.CLIENT_SECRET,
                    'grant_type': 'refresh_token',
                    'refresh_token': settings.STRAVA_REFRESH_TOKEN
                }
            )
            if response.status_code == http.HTTPStatus.OK:
                new_strava_tokens = response.json()
                if new_strava_tokens:
                    self.strava_token.access_token = (
                        new_strava_tokens['access_token'])
                    self.strava_token.expires_at = \
                        new_strava_tokens['expires_at']
                    self.strava_token.save()
                else:
                    raise StravaExternalException('Strava response contained '
                                                  'no data')
            else:
                raise StravaExternalException('Strava response was not OK.')
        self.access_token = self.strava_token.access_token


class Athlete(StravaBase):

    def _make_athlete_request(self, url):
        header = {"Authorization": f"Bearer {self.access_token}"}
        r = requests.get(url, headers=header)
        if r.status_code == http.HTTPStatus.OK:
            return r.json()

    def athlete(self):
        athlete = self.get_athlete_stats()
        athlete.update(self.get_athlete_profile())
        return athlete

    def get_athlete_goal_progress(self, ride_target=3000,
                                  run_target=1000, stats=None):
        return_goals = {}
        if not stats:
            stats = self._make_athlete_request(settings.ATHLETE_STATS_URL)
        ytd_ride_miles = round((stats['ytd_ride_totals']['distance']
                                * METERS_TO_MILES), 2)
        ytd_run_miles = round((stats['ytd_run_totals']['distance']
                               * METERS_TO_MILES), 2)
        ride_progress = round((ytd_ride_miles / ride_target) * 100, 2)
        run_progress = round((ytd_run_miles / run_target) * 100, 2)
        return_goals['ride'] = {'target': ride_target,
                                'ytd': ytd_ride_miles,
                                'progress': ride_progress}
        return_goals['run'] = {'target': run_target,
                               'ytd': ytd_run_miles,
                               'progress': run_progress}
        return return_goals

    def get_athlete_profile(self):
        return self._make_athlete_request(settings.ATHLETE_URL)

    def get_athlete_stats(self):
        stats = self._make_athlete_request(settings.ATHLETE_STATS_URL)
        stats['goals'] = self.get_athlete_goal_progress(stats=stats)
        return stats


class Strava(StravaBase):

    def __init__(self):
        super(Strava, self).__init__()
        self.activities = []

    def get_past_activities(self, days=30):
        self.activities = []
        today = datetime.datetime.now()
        delta = datetime.timedelta(days=days)
        past_timestamp = int((today - delta).timestamp())
        page = 1
        while True:
            url = (f'{settings.ACTIVITIES_URL}?'
                   f'access_token={self.access_token}&'
                   f'per_page=200&page={str(page)}&'
                   f'after={past_timestamp}')
            r = requests.get(url)
            if r.status_code == 200:
                r = r.json()
                if r:
                    self.activities.extend(r)
                    page += 1
                else:
                    break
            else:
                break
        return self.activities

    def get_organized_activities(self, days=30):
        base = datetime.datetime.today()
        date_list = {}
        for x in range(days+1):
            date_list[(base - datetime.timedelta(
                days=x)).strftime("%Y-%m-%d")] = []
        data = self.get_past_activities(days=days)
        for item in data:
            name = item.get('name')
            activity_type = item.get('type').lower()
            distance = item.get('distance')
            elevation_gain = item.get('total_elevation_gain')
            moving_time = item.get('moving_time')
            start_date = datetime.datetime.strptime(
                item.get('start_date_local'), '%Y-%m-%dT%H:%M:%SZ')
            a = Activity(name=name, activity_type=activity_type,
                         distance=distance, elevation_gain=elevation_gain,
                         moving_time=moving_time, start_date=start_date)
            date_list[a.get_activity_date()].append(a.to_dict())
        return date_list

    def get_all_activities(self):
        page = 1
        while True:
            r = requests.get(settings.ACTIVITIES_URL + '?access_token=' +
                             self.access_token + '&per_page=200'
                             + '&page=' + str(page))
            if r:
                r = r.json()
                self.activities.extend(r)
                page += 1
            else:
                break
        return self.activities

    def get_recent_activities(self, days=30):
        data = self.get_past_activities(days=days)
        original_longest_run = longest_run = self.peaks.longest_run
        original_longest_ride = longest_ride = self.peaks.longest_ride
        longest_ride_date = self.peaks.longest_ride_date
        longest_run_date = self.peaks.longest_run_date
        recent_ride = {'timestamp': 0}
        recent_run = {'timestamp': 0}
        for item in data:
            start_date_local = datetime.datetime.strptime(
                item.get('start_date_local'), '%Y-%m-%dT%H:%M:%SZ')
            timestamp = datetime.datetime.timestamp(start_date_local)
            if (timestamp > recent_ride.get('timestamp')
                    and item.get('type') == 'Ride'):
                recent_ride['timestamp'] = timestamp
                item['map'] = None
                if item['distance'] > longest_ride:
                    longest_ride = item['distance']
                    # TODO: fix timezone warning
                    longest_ride_date = datetime.datetime.strptime(
                        item.get('start_date'), '%Y-%m-%dT%H:%M:%SZ')
                recent_ride.update(item)
            elif (timestamp > recent_run.get('timestamp')
                    and item.get('type') == 'Run'):
                recent_run['timestamp'] = timestamp
                item['map'] = None
                if item['distance'] > longest_run:
                    longest_run = item['distance']
                    # TODO: fix timezone warning
                    longest_run_date = datetime.datetime.strptime(
                        item.get('start_date'), '%Y-%m-%dT%H:%M:%SZ')

                recent_run.update(item)
        if (original_longest_ride != longest_ride or
                original_longest_run != longest_run):
            self.peaks.longest_ride = longest_ride
            self.peaks.longest_run = longest_run
            self.peaks.longest_ride_date = longest_ride_date
            self.peaks.longest_run_date = longest_run_date
            self.peaks.save()
        peaks_serialized = PeaksSerializer(self.peaks).data

        return_dict = {'recent_run': recent_run,
                       'recent_ride': recent_ride,
                       'longest_run': longest_run,
                       'longest_ride': longest_ride}
        return_dict.update(peaks_serialized)
        return return_dict
