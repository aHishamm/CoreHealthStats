from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    HealthDataUpload, HealthRecord, Workout, 
    DailyMetrics, NightlyMetrics, UserProfile
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = UserProfile
        fields = ['user', 'age', 'gender', 'timezone']


class HealthDataUploadSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    record_count = serializers.SerializerMethodField()
    workout_count = serializers.SerializerMethodField()
    
    class Meta:
        model = HealthDataUpload
        fields = [
            'id', 'user', 'file', 'uploaded_at', 'processed', 
            'processing_error', 'record_count', 'workout_count'
        ]
        read_only_fields = ['id', 'uploaded_at', 'processed', 'processing_error']
    
    def get_record_count(self, obj):
        return obj.records.count()
    
    def get_workout_count(self, obj):
        return obj.workouts.count()


class HealthRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthRecord
        fields = [
            'id', 'type', 'value', 'unit', 'start_date', 
            'end_date', 'creation_date'
        ]
        read_only_fields = ['id']


class WorkoutSerializer(serializers.ModelSerializer):
    heart_rate_stats = serializers.SerializerMethodField()
    
    class Meta:
        model = Workout
        fields = [
            'id', 'activity_type', 'duration', 'start_date', 
            'end_date', 'creation_date', 'avg_heart_rate', 
            'trimp_score', 'heart_rate_stats'
        ]
        read_only_fields = ['id', 'avg_heart_rate', 'trimp_score']
    
    def get_heart_rate_stats(self, obj):
        # This will be populated by the view if requested
        return getattr(obj, '_heart_rate_stats', None)


class DailyMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = DailyMetrics
        fields = [
            'id', 'date', 'steps', 'steps_7day_avg', 'step_streak',
            'resting_hr', 'basal_energy_kcal', 'active_energy_kcal', 
            'total_energy_kcal', 'hrv_sdnn', 'hrv_baseline', 
            'hrv_z_score', 'vo2_max', 'met_minutes'
        ]
        read_only_fields = ['id']


class NightlyMetricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NightlyMetrics
        fields = [
            'id', 'date', 'respiratory_rate_mean', 'respiratory_rate_baseline',
            'respiratory_rate_z_score', 'respiratory_rate_elevated',
            'spo2_median', 'spo2_p01', 'pct_time_below_90',
            'wrist_temp', 'temp_baseline', 'temp_deviation'
        ]
        read_only_fields = ['id']


class WorkoutAnalysisSerializer(serializers.Serializer):
    """Serializer for workout analysis results"""
    workout_id = serializers.IntegerField()
    heart_rate_stats = serializers.DictField()
    trimp_score = serializers.FloatField(allow_null=True)
    activity_type = serializers.CharField()
    duration = serializers.FloatField()
    start_date = serializers.DateTimeField()


class HealthSummarySerializer(serializers.Serializer):
    """Serializer for health data summary"""
    upload_id = serializers.UUIDField()
    date_range = serializers.DictField()
    total_records = serializers.IntegerField()
    total_workouts = serializers.IntegerField()
    available_metrics = serializers.ListField(child=serializers.CharField())
    latest_metrics = serializers.DictField()


class DateRangeFilterSerializer(serializers.Serializer):
    """Serializer for date range filtering"""
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    metric_type = serializers.ChoiceField(
        choices=[
            ('steps', 'Steps'),
            ('heart_rate', 'Heart Rate'),
            ('energy', 'Energy'),
            ('hrv', 'Heart Rate Variability'),
            ('respiratory_rate', 'Respiratory Rate'),
            ('spo2', 'Blood Oxygen'),
            ('temperature', 'Temperature'),
            ('vo2_max', 'VO2 Max'),
        ],
        required=False
    )


class WorkoutFilterSerializer(serializers.Serializer):
    """Serializer for workout filtering"""
    activity_type = serializers.CharField(required=False)
    start_date = serializers.DateField(required=False)
    end_date = serializers.DateField(required=False)
    min_duration = serializers.FloatField(required=False)
    max_duration = serializers.FloatField(required=False)
    include_heart_rate = serializers.BooleanField(default=False)
