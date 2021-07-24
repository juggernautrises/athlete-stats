from rest_framework import serializers
from stats.models import Mood


class MoodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mood
        fields = ['id', 'number', 'mood_date']


class PeaksSerializer(serializers.Serializer):
    longest_run = serializers.FloatField(default=0.0)
    longest_ride = serializers.FloatField(default=0.0)
    longest_run_date = serializers.DateTimeField()
    longest_ride_date = serializers.DateTimeField()
