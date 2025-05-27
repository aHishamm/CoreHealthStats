from django.db import models
from django.contrib.auth.models import User
import uuid


class HealthDataUpload(models.Model):
    """Model to track uploaded health data files"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='health_exports/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processed = models.BooleanField(default=False)
    processing_error = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-uploaded_at']


class HealthRecord(models.Model):
    """Model for individual health records from Apple Health"""
    upload = models.ForeignKey(HealthDataUpload, on_delete=models.CASCADE, related_name='records')
    type = models.CharField(max_length=100, db_index=True)
    value = models.FloatField()
    unit = models.CharField(max_length=50, blank=True)
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField()
    creation_date = models.DateTimeField()
    
    class Meta:
        ordering = ['-start_date']
        indexes = [
            models.Index(fields=['type', 'start_date']),
            models.Index(fields=['upload', 'type']),
        ]


class Workout(models.Model):
    """Model for workout data from Apple Health"""
    upload = models.ForeignKey(HealthDataUpload, on_delete=models.CASCADE, related_name='workouts')
    activity_type = models.CharField(max_length=100, db_index=True)
    duration = models.FloatField()  # in minutes
    start_date = models.DateTimeField(db_index=True)
    end_date = models.DateTimeField()
    creation_date = models.DateTimeField()
    
    # Additional computed fields
    avg_heart_rate = models.FloatField(null=True, blank=True)
    trimp_score = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-start_date']


class DailyMetrics(models.Model):
    """Model for daily aggregated health metrics"""
    upload = models.ForeignKey(HealthDataUpload, on_delete=models.CASCADE, related_name='daily_metrics')
    date = models.DateField(db_index=True)
    
    # Step count metrics
    steps = models.IntegerField(null=True, blank=True)
    steps_7day_avg = models.FloatField(null=True, blank=True)
    step_streak = models.IntegerField(null=True, blank=True)
    
    # Heart rate metrics
    resting_hr = models.FloatField(null=True, blank=True)
    
    # Energy metrics
    basal_energy_kcal = models.FloatField(null=True, blank=True)
    active_energy_kcal = models.FloatField(null=True, blank=True)
    total_energy_kcal = models.FloatField(null=True, blank=True)
    
    # HRV metrics
    hrv_sdnn = models.FloatField(null=True, blank=True)
    hrv_baseline = models.FloatField(null=True, blank=True)
    hrv_z_score = models.FloatField(null=True, blank=True)
    
    # VO2 Max
    vo2_max = models.FloatField(null=True, blank=True)
    
    # MET minutes
    met_minutes = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['upload', 'date']


class NightlyMetrics(models.Model):
    """Model for nightly aggregated health metrics"""
    upload = models.ForeignKey(HealthDataUpload, on_delete=models.CASCADE, related_name='nightly_metrics')
    date = models.DateField(db_index=True)
    
    # Respiratory rate metrics
    respiratory_rate_mean = models.FloatField(null=True, blank=True)
    respiratory_rate_baseline = models.FloatField(null=True, blank=True)
    respiratory_rate_z_score = models.FloatField(null=True, blank=True)
    respiratory_rate_elevated = models.BooleanField(default=False)
    
    # SpO2 metrics
    spo2_median = models.FloatField(null=True, blank=True)
    spo2_p01 = models.FloatField(null=True, blank=True)
    pct_time_below_90 = models.FloatField(null=True, blank=True)
    
    # Temperature metrics
    wrist_temp = models.FloatField(null=True, blank=True)
    temp_baseline = models.FloatField(null=True, blank=True)
    temp_deviation = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ['-date']
        unique_together = ['upload', 'date']


class UserProfile(models.Model):
    """Extended user profile for health-specific information"""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    age = models.PositiveIntegerField(null=True, blank=True)
    gender = models.CharField(
        max_length=10, 
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        default='male'
    )
    timezone = models.CharField(max_length=50, default='UTC')
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
