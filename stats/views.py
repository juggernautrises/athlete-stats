import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets


from stats.strava import Athlete, Strava


class AthleteView(APIView):

    def get(self, request, pk=None):
        a = Athlete()
        return Response(a.athlete())


class ActivityView(viewsets.ViewSet):

    def list(self, request):
        s = Strava()
        return Response(s.get_organized_activities())

    def recent(self, request):
        return Response(Strava().get_recent_activities())
