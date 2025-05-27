from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.db.models import Q, Count, Avg, Max, Min
from django.utils.dateparse import parse_date
from django.contrib.auth.models import User
from datetime import datetime, timedelta
import pandas as pd

from .models import (
    HealthDataUpload, HealthRecord, Workout, 
    DailyMetrics, NightlyMetrics, UserProfile
)
from .serializers import (
    HealthDataUploadSerializer, HealthRecordSerializer, WorkoutSerializer,
    DailyMetricsSerializer, NightlyMetricsSerializer, UserProfileSerializer,
    WorkoutAnalysisSerializer, HealthSummarySerializer, DateRangeFilterSerializer,
    WorkoutFilterSerializer
)
from .services import HealthDataProcessor, HealthAnalyticsService


class HealthDataUploadViewSet(viewsets.ModelViewSet):
    """ViewSet for managing health data uploads"""
    serializer_class = HealthDataUploadSerializer
    parser_classes = (MultiPartParser, FormParser)
    permission_classes = [permissions.AllowAny]  # Change to IsAuthenticated in production
    
    def get_queryset(self):
        # Filter by user if authenticated, otherwise return all 
        if self.request.user.is_authenticated:
            return HealthDataUpload.objects.filter(user=self.request.user)
        return HealthDataUpload.objects.all()
    
    def perform_create(self, serializer):
        # Associate upload with current user if authenticated
        user = self.request.user if self.request.user.is_authenticated else None
        upload = serializer.save(user=user)
        
        # Process the uploaded file asynchronously
        self._process_upload(upload)
    
    def _process_upload(self, upload):
        """Process the uploaded health data file"""
        try:
            processor = HealthDataProcessor(upload)
            success, message = processor.process_uploaded_file()
            
            upload.processed = success
            if not success:
                upload.processing_error = message
            upload.save()
            
        except Exception as e:
            upload.processed = False
            upload.processing_error = str(e)
            upload.save()
    
    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get summary statistics for an uploaded dataset"""
        upload = self.get_object()
        
        if not upload.processed:
            return Response(
                {"error": "Upload not yet processed or failed to process"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get date range
        records = upload.records.all()
        workouts = upload.workouts.all()
        
        if not records.exists():
            return Response(
                {"error": "No health records found"},
                status=status.HTTP_404_NOT_FOUND
            )
        
        date_range = {
            'start_date': records.aggregate(Min('start_date'))['start_date__min'],
            'end_date': records.aggregate(Max('start_date'))['start_date__max']
        }
        
        # Get available metric types
        available_metrics = list(records.values_list('type', flat=True).distinct())
        
        # Get latest metrics
        latest_daily = DailyMetrics.objects.filter(upload=upload).order_by('-date').first()
        latest_nightly = NightlyMetrics.objects.filter(upload=upload).order_by('-date').first()
        
        latest_metrics = {}
        if latest_daily:
            latest_metrics['daily'] = DailyMetricsSerializer(latest_daily).data
        if latest_nightly:
            latest_metrics['nightly'] = NightlyMetricsSerializer(latest_nightly).data
        
        summary_data = {
            'upload_id': upload.id,
            'date_range': date_range,
            'total_records': records.count(),
            'total_workouts': workouts.count(),
            'available_metrics': available_metrics,
            'latest_metrics': latest_metrics
        }
        
        serializer = HealthSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reprocess(self, request, pk=None):
        """Reprocess an uploaded file"""
        upload = self.get_object()
        
        # Clear existing processed data
        upload.processed = False
        upload.processing_error = None
        upload.save()
        
        # Reprocess
        self._process_upload(upload)
        
        return Response({"message": "Reprocessing initiated"})


class HealthRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing health records"""
    serializer_class = HealthRecordSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = HealthRecord.objects.all()
        
        # Filter by upload
        upload_id = self.request.query_params.get('upload', None)
        if upload_id:
            queryset = queryset.filter(upload_id=upload_id)
        
        # Filter by type
        record_type = self.request.query_params.get('type', None)
        if record_type:
            queryset = queryset.filter(type=record_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(start_date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(start_date__lte=parse_date(end_date))
        
        return queryset.order_by('-start_date')
    
    @action(detail=False, methods=['get'])
    def types(self, request):
        """Get available health record types"""
        upload_id = request.query_params.get('upload', None)
        queryset = HealthRecord.objects.all()
        
        if upload_id:
            queryset = queryset.filter(upload_id=upload_id)
        
        types = queryset.values_list('type', flat=True).distinct().order_by('type')
        return Response(list(types))


class WorkoutViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing workouts"""
    serializer_class = WorkoutSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = Workout.objects.all()
        
        # Filter by upload
        upload_id = self.request.query_params.get('upload', None)
        if upload_id:
            queryset = queryset.filter(upload_id=upload_id)
        
        # Filter by activity type
        activity_type = self.request.query_params.get('activity_type', None)
        if activity_type:
            queryset = queryset.filter(activity_type=activity_type)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(start_date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(start_date__lte=parse_date(end_date))
        
        # Filter by duration
        min_duration = self.request.query_params.get('min_duration', None)
        max_duration = self.request.query_params.get('max_duration', None)
        
        if min_duration:
            queryset = queryset.filter(duration__gte=float(min_duration))
        if max_duration:
            queryset = queryset.filter(duration__lte=float(max_duration))
        
        return queryset.order_by('-start_date')
    
    @action(detail=True, methods=['get'])
    def heart_rate_analysis(self, request, pk=None):
        """Get detailed heart rate analysis for a workout"""
        workout = self.get_object()
        
        # Get user age for heart rate zone calculations
        user_age = None
        if workout.upload.user and hasattr(workout.upload.user, 'userprofile'):
            user_age = workout.upload.user.userprofile.age
        
        # Get heart rate analysis
        hr_stats = HealthAnalyticsService.get_workout_heart_rate_analysis(
            workout.id, user_age=user_age
        )
        
        if 'error' in hr_stats:
            return Response(hr_stats, status=status.HTTP_404_NOT_FOUND)
        
        return Response(hr_stats)
    
    @action(detail=True, methods=['post'])
    def calculate_trimp(self, request, pk=None):
        """Calculate TRIMP score for a workout"""
        workout = self.get_object()
        
        # Get user gender for TRIMP calculation
        user_gender = 'male'  # default
        if workout.upload.user and hasattr(workout.upload.user, 'userprofile'):
            user_gender = workout.upload.user.userprofile.gender
        
        # Calculate TRIMP
        trimp = HealthAnalyticsService.calculate_trimp_for_workout(
            workout.id, user_gender=user_gender
        )
        
        if trimp is None:
            return Response(
                {"error": "Could not calculate TRIMP score"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({"trimp_score": trimp})
    
    @action(detail=False, methods=['get'])
    def activity_types(self, request):
        """Get available workout activity types"""
        upload_id = request.query_params.get('upload', None)
        queryset = Workout.objects.all()
        
        if upload_id:
            queryset = queryset.filter(upload_id=upload_id)
        
        types = queryset.values_list('activity_type', flat=True).distinct().order_by('activity_type')
        return Response(list(types))


class DailyMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing daily metrics"""
    serializer_class = DailyMetricsSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = DailyMetrics.objects.all()
        
        # Filter by upload
        upload_id = self.request.query_params.get('upload', None)
        if upload_id:
            queryset = queryset.filter(upload_id=upload_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(date__lte=parse_date(end_date))
        
        return queryset.order_by('-date')
    
    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get trending data for charts"""
        upload_id = request.query_params.get('upload', None)
        metric = request.query_params.get('metric', 'steps')
        days = int(request.query_params.get('days', 30))
        
        if not upload_id:
            return Response(
                {"error": "Upload ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=days)
        
        queryset = DailyMetrics.objects.filter(
            upload_id=upload_id,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Get the requested metric
        data = []
        for metric_obj in queryset:
            value = getattr(metric_obj, metric, None)
            if value is not None:
                data.append({
                    'date': metric_obj.date,
                    'value': value
                })
        
        return Response(data)


class NightlyMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing nightly metrics"""
    serializer_class = NightlyMetricsSerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        queryset = NightlyMetrics.objects.all()
        
        # Filter by upload
        upload_id = self.request.query_params.get('upload', None)
        if upload_id:
            queryset = queryset.filter(upload_id=upload_id)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date', None)
        end_date = self.request.query_params.get('end_date', None)
        
        if start_date:
            queryset = queryset.filter(date__gte=parse_date(start_date))
        if end_date:
            queryset = queryset.filter(date__lte=parse_date(end_date))
        
        return queryset.order_by('-date')


class UserProfileViewSet(viewsets.ModelViewSet):
    """ViewSet for managing user profiles"""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.AllowAny]  # Change to IsAuthenticated in production
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return UserProfile.objects.filter(user=self.request.user)
        return UserProfile.objects.all()
    
    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
