from django.urls import path
from stats import views

urlpatterns = [
    path('activities/', views.ActivityView.as_view({'get': 'list'})),
    path('athlete/', views.AthleteView.as_view()),
    path('recent/', views.ActivityView.as_view({'get': 'recent'})),
]
