import datetime
import http
import json
import os
from pathlib import Path
from django.conf import settings
from django.test import TestCase
from stats.exceptions import StravaExternalException
from stats.strava import Athlete, StravaBase
from stats.models import Peaks, StravaToken
from unittest import mock


class StravaBaseTestCase(TestCase):
    # Test has peaks
    # Test no peaks
    # Test no strava token
    # Test expired token
    # Test responses
    def setUp(self):
        expires_at = datetime.datetime.now() - datetime.timedelta(days=30)
        self.strava_token = StravaToken(
            access_token=settings.STRAVA_DEFAULT_ACCESS_TOKEN,
            expires_at=int(expires_at.timestamp()))
        self.strava_token.save()

    def test_200_empty_response(self):
        self.assertEqual(Peaks.objects.all().count(), 0)
        with mock.patch('stats.strava.requests') as mock_requests:
            mock_requests.post.return_value.json.return_value = {}
            mock_requests.post.return_value.status_code = http.HTTPStatus.OK
            self.assertRaises(StravaExternalException, StravaBase)

    def test_500_with_response(self):
        self.assertEqual(Peaks.objects.all().count(), 0)
        with mock.patch('stats.strava.requests') as mock_requests:
            mock_requests.post.return_value.json.return_value = {"id": 1}
            mock_requests.post.return_value.status_code = \
                http.HTTPStatus.SERVICE_UNAVAILABLE
            self.assertRaises(StravaExternalException, StravaBase)


class AthleteTestCase(TestCase):
    root_dir = Path(__file__).resolve().parent
    activity_response_file = os.path.join(root_dir,
                                          'response_json',
                                          'activities.json')
    athlete_response_file = os.path.join(root_dir,
                                         'response_json',
                                         'athlete.json')
    stats_response_file = os.path.join(root_dir,
                                       'response_json',
                                       'stats.json')

    activity_response = json.load(open(activity_response_file, 'r'))
    athlete_response = json.load(open(athlete_response_file, 'r'))
    stats_response = json.load(open(stats_response_file, 'r'))

    def setUp(self):
        expires_at = datetime.datetime.now() + datetime.timedelta(days=30)
        self.strava_token = StravaToken(
            access_token=settings.STRAVA_DEFAULT_ACCESS_TOKEN,
            expires_at=int(expires_at.timestamp()))
        self.strava_token.save()

    @mock.patch.object(Athlete, '_make_athlete_request',
                       return_value=athlete_response)
    def test_get_athlete_profile(self, mock_athlete_requests):
        self.assertEqual(Peaks.objects.all().count(), 0)
        a = Athlete()
        profile = a.get_athlete_profile()
        self.assertNotEqual(profile.get('id'), None)
        self.assertNotEqual(profile.get('profile'), None)
        self.assertNotEqual(profile.get('bikes'), None)
        self.assertNotEqual(profile.get('shoes'), None)

    @mock.patch.object(Athlete, '_make_athlete_request',
                       return_value=stats_response)
    def test_get_athlete_goal_progress_no_stats(self, mock_stats_response):
        class AthleteTestClass(Athlete):
            def __init__(self):
                pass
        a = AthleteTestClass()
        progress = a.get_athlete_goal_progress()
        self.assertEqual(progress['ride']['target'], 3000)
        self.assertEqual(progress['ride']['ytd'], 523.77)
        self.assertEqual(progress['ride']['progress'], 17.46)
        self.assertEqual(progress['run']['target'], 1000)
        self.assertEqual(progress['run']['ytd'], 98.65)
        self.assertEqual(progress['run']['progress'], 9.87)

    def test_get_athlete_goal_progress_with_stats(self):
        class AthleteTestClass(Athlete):
            def __init__(self):
                pass
        a = AthleteTestClass()
        stats = {
            'ytd_ride_totals': {'distance': 420},
            'ytd_run_totals': {'distance': 50}
        }
        progress = a.get_athlete_goal_progress(run_target=500,
                                               ride_target=500,
                                               stats=stats)
        self.assertEqual(progress['ride']['target'], 500)
        self.assertEqual(progress['ride']['ytd'], .26)
        self.assertEqual(progress['ride']['progress'], .05)
        self.assertEqual(progress['run']['target'], 500)
        self.assertEqual(progress['run']['ytd'], .03)
        self.assertEqual(progress['run']['progress'], .01)

    @mock.patch.object(Athlete, '_make_athlete_request',
                       return_value=stats_response)
    def test_get_athlete_stats(self, mock_stats_response):
        class AthleteTestClass(Athlete):
            def __init__(self):
                pass
        a = AthleteTestClass()
        stats = a.get_athlete_stats()
        self.assertNotEqual(stats.get('goals'), None)
