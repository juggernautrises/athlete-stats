from rest_framework import serializers


class PeaksSerializer(serializers.Serializer):
    longest_run = serializers.FloatField(default=0.0)
    longest_ride = serializers.FloatField(default=0.0)
    longest_run_date = serializers.DateTimeField()
    longest_ride_date = serializers.DateTimeField()
