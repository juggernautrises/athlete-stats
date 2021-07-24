import redis
from django.conf import settings
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.views import APIView
from stats.strava import Athlete, Strava
from stats.models import Mood
from stats.serializers import MoodSerializer


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


class Home(APIView):
    renderer_classes = [StaticHTMLRenderer]

    def get(self, request):
        data = ('<html>'
                '<body>'
                '<img src="https://i.imgur.com/HPJGhpZ.jpg">'
                '</body>'
                '</html>')
        return Response(data)


class MoodView(viewsets.ViewSet):

    def list(self, request):
        month = self.request.query_params.get('month')
        if month:
            moods = (Mood.objects.filter(mood_date__month=month))
            return Response(MoodSerializer(moods, many=True).data)
        return Response(MoodSerializer(Mood.objects.all(),  many=True).data)

    def retrieve(self, request, pk):
        return Response({"pk": pk})

    def post(self, request):
        response = {}
        # Ideally this would be moved into a controller
        # but it's small enough to keep here for now
        if request.data:
            # This would need a separate validator function
            for item in ['day', 'month', 'year', 'number']:
                if item not in request.data:
                    return Response({'message': 'Missing required data.'})

            data = request.data
            month = data.get('month')
            day = data.get('day')
            year = data.get('year')
            number = data.get('number')
            dt = datetime.datetime(year=year, month=month, day=day)
            mood = Mood.objects.filter(mood_date=dt)
            if mood:
                return Response(MoodSerializer(mood.first()).data)

            mood = Mood(mood_date=dt, number=number)
            mood.save()
            response = MoodSerializer(mood).data
        return Response(response)


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
