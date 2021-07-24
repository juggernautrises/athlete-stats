from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views
from stats import views

urlpatterns = [
    path('activities/', views.ActivityView.as_view({'get': 'list'})),
    path('athlete/', views.AthleteView.as_view()),
    path('goals/', views.GoalView.as_view()),
    path('mood/', views.MoodView.as_view({'get': 'list', 'post': 'post'})),
    path('recent/', views.ActivityView.as_view({'get': 'recent'})),
    path('spongebob/'
         '', views.SpongeBobView.as_view())
]

# API Tokens
urlpatterns += [
    path('token/',
         jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/',
         jwt_views.TokenRefreshView.as_view(),
         name='token_refresh')
]

# Swagger Docs
schema_view = get_schema_view(
    openapi.Info(
        title="Athlete Stats API",
        default_version='v1',
        description="For retrieving Strava stats",
        contact=openapi.Contact(email="ashoknayar@gmail.com"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns += [
    re_path(r'^docs(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('docs/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redocs/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
