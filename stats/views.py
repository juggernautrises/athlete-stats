from stats.strava import Athlete, Strava

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated


class AthleteView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, pk=None):
        a = Athlete()
        return Response(a.athlete())


class ActivityView(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        s = Strava()
        return Response(s.get_organized_activities())

    def recent(self, request):
        return Response(Strava().get_recent_activities())
