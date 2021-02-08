import datetime
import http
import requests

from stats.constants import METERS_TO_FEET, METERS_TO_MILES
from stats.models import StravaToken
from athlete_stats.settings import (ACTIVITIES_URL, ATHLETE_URL,
                                    ATHLETE_STATS_URL, CLIENT_ID,
                                    CLIENT_SECRET, OATH_TOKEN_URL)


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
        strava_token = StravaToken.objects.first()
        if strava_token.is_expired:
            response = requests.post(
                url=OATH_TOKEN_URL,
                data={
                    'client_id': CLIENT_ID,
                    'client_secret': CLIENT_SECRET,
                    'grant_type': 'refresh_token',
                    'refresh_token': strava_token.refresh_token
                }
            )
            new_strava_tokens = response.json()
            self.strava_tokens = new_strava_tokens
            strava_token.refresh_token = self.strava_tokens['refresh_token']
            strava_token.expires_at = self.strava_tokens['expires_at']


class Athlete(StravaBase):
    def _make_athlete_request(self, url):
        access_token = self.strava_tokens['access_token']
        header = {"Authorization": f"Bearer {access_token}"}
        r = requests.get(url, headers=header)
        if r.status_code == http.HTTPStatus.OK:
            return r.json()

    def get_athlete_profile(self):
        return self._make_athlete_request(ATHLETE_URL)

    def get_athlete_stats(self):
        return self._make_athlete_request(ATHLETE_STATS_URL)

    def athlete(self):
        athlete = self.get_athlete_stats()
        athlete.update(self.get_athlete_profile())
        return athlete


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
        access_token = self.strava_tokens['access_token']
        while True:
            url = f'{ACTIVITIES_URL}?access_token={access_token}&' \
                  f'per_page=200&page={str(page)}&after={past_timestamp}'
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
        for x in range(days):
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
        access_token = self.strava_tokens['access_token']
        while True:
            r = requests.get(ACTIVITIES_URL + '?access_token=' +
                             access_token + '&per_page=200'
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
                recent_ride.update(item)
            elif (timestamp > recent_run.get('timestamp')
                    and item.get('type') == 'Run'):
                recent_run['timestamp'] = timestamp
                item['map'] = None
                recent_run.update(item)
        return {'recent_run': recent_run,
                'recent_ride': recent_ride}
