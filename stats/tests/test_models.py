import datetime
from django.test import TestCase
from stats.models import Peaks, StravaToken


class PeaksTestCase(TestCase):
    def setUp(self):
        self.activity_date = (datetime.datetime.utcnow()
                              - datetime.timedelta(seconds=60))

        self.default_peaks = Peaks.objects.create()
        self.long_run_peak = Peaks.objects.create(
            longest_run=23.56,
        )
        self.long_ride_peak = Peaks.objects.create(
            longest_ride=63.45,
        )
        self.long_ride_date = Peaks.objects.create(
            longest_ride=120.56,
            longest_ride_date=self.activity_date
        )
        self.long_run_date = Peaks.objects.create(
            longest_run=13.1,
            longest_run_date=self.activity_date
        )

    def test_peaks_default(self):
        self.assertEqual(0.0, self.default_peaks.longest_run)
        self.assertEqual(0.0, self.default_peaks.longest_ride)
        self.assertNotEqual(None, self.default_peaks.longest_ride_date)
        self.assertNotEqual(None, self.default_peaks.longest_run_date)

    def test_peaks_longest_run(self):
        self.assertEqual(23.56, self.long_run_peak.longest_run)
        self.assertNotEqual(None, self.long_run_peak.longest_ride_date)
        self.assertNotEqual(None, self.long_run_peak.longest_run_date)

    def test_peaks_longest_ride(self):
        self.assertEqual(63.45, self.long_ride_peak.longest_ride)
        self.assertNotEqual(None, self.long_ride_peak.longest_ride_date)
        self.assertNotEqual(None, self.long_ride_peak.longest_run_date)

    def test_peaks_longest_run_date(self):
        self.assertEqual(13.1, self.long_run_date.longest_run)
        self.assertEqual(self.activity_date,
                         self.long_run_date.longest_run_date)
        self.assertNotEqual(self.activity_date,
                            self.long_run_peak.longest_ride_date)

    def test_peaks_longest_ride_date(self):
        self.assertEqual(120.56, self.long_ride_date.longest_ride)
        self.assertEqual(self.activity_date,
                         self.long_ride_date.longest_ride_date)
        self.assertNotEqual(self.activity_date,
                            self.long_run_peak.longest_run_date)


class StravaTokenTestCase(TestCase):
    def setUp(self):
        self.not_expired = StravaToken.objects.create(
            access_token='not_expired_token',
            expires_at=datetime.datetime.timestamp(
                datetime.datetime.now() + datetime.timedelta(days=30))
        )

        self.expired_model = StravaToken.objects.create(
            access_token='expired_token',
            expires_at=datetime.datetime.timestamp(
                datetime.datetime.now() - datetime.timedelta(days=30))
        )

    def test_expired_token(self):
        self.assertGreater(datetime.datetime.timestamp(
            datetime.datetime.now()), self.expired_model.expires_at)
        self.assertEqual('expired_token', self.expired_model.access_token)
        self.assertEqual(True, self.expired_model.is_expired)

    def test_not_expired_token(self):
        self.assertLess(datetime.datetime.timestamp(datetime.datetime.now()),
                        self.not_expired.expires_at)
        self.assertEqual('not_expired_token', self.not_expired.access_token)
        self.assertEqual(False, self.not_expired.is_expired)
