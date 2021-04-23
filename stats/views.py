from stats.strava import Athlete, Strava
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


class ActivityView(viewsets.ViewSet):
    # permission_classes = (IsAuthenticated,)

    # TODO: add optional days parameter
    def list(self, request):
        """Returns a JSON object of the past 30 days of activities.
        Keys are the dates and the values are list of activities for
        that date.
        Example:
            {'2020-03-08': []}
        Args:
            request: request object

        Returns:
            JSON object of activities organized by date.

        """
        s = Strava()
        return Response(s.get_organized_activities())

    def recent(self, request):
        """Returns JSON object containing the most recent ride
        and run within the last 30 days.
        Args:
            request: request object

        Returns:
            JSON dictionary of the most recent run and ride.
        """
        return Response(Strava().get_recent_activities())


class AthleteView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Returns all relevant athlete information such as
        profile information, gear information, and general ride
        statistics.
        Args:
            request: request object

        Returns:
            JSON dictionary of athlete information.
        """
        a = Athlete()
        return Response(a.athlete())


class GoalView(APIView):
    # permission_classes = (IsAuthenticated,)

    def get(self, request):
        """Returns run and ride goals and progress.
        Args:
            request: request object

        Returns:
            JSON dictionary of run and ride goals.
        """
        a = Athlete()
        return Response(a.get_athlete_goal_progress())


class SpongeBobView(APIView):

    def post(self, request):
        return_text = ''
        input_text = request.data.get('text')
        if input_text:
            upper = False
            input_text = input_text.strip()
            for char in input_text:
                if char.isalpha():
                    if upper:
                        return_text += char.upper()
                        upper = False
                    else:
                        return_text += char.lower()
                        upper = True
                else:
                    return_text += char

        return Response(return_text)
