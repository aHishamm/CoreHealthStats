from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'uploads', views.HealthDataUploadViewSet, basename='upload')
router.register(r'records', views.HealthRecordViewSet, basename='record')
router.register(r'workouts', views.WorkoutViewSet, basename='workout')
router.register(r'daily-metrics', views.DailyMetricsViewSet, basename='daily-metrics')
router.register(r'nightly-metrics', views.NightlyMetricsViewSet, basename='nightly-metrics')
router.register(r'profiles', views.UserProfileViewSet, basename='profile')

urlpatterns = [
    path('api/', include(router.urls)),
]
