from django.contrib import admin
from .models import (
    HealthDataUpload, HealthRecord, Workout, 
    DailyMetrics, NightlyMetrics, UserProfile
)


@admin.register(HealthDataUpload)
class HealthDataUploadAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'uploaded_at', 'processed', 'get_record_count', 'get_workout_count']
    list_filter = ['processed', 'uploaded_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['id', 'uploaded_at']
    
    def get_record_count(self, obj):
        return obj.records.count()
    get_record_count.short_description = 'Records'
    
    def get_workout_count(self, obj):
        return obj.workouts.count()
    get_workout_count.short_description = 'Workouts'


@admin.register(HealthRecord)
class HealthRecordAdmin(admin.ModelAdmin):
    list_display = ['id', 'upload', 'type', 'value', 'unit', 'start_date']
    list_filter = ['type', 'start_date', 'upload']
    search_fields = ['type', 'upload__user__username']
    date_hierarchy = 'start_date'
    readonly_fields = ['id']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('upload', 'upload__user')


@admin.register(Workout)
class WorkoutAdmin(admin.ModelAdmin):
    list_display = ['id', 'upload', 'activity_type', 'duration', 'start_date', 'avg_heart_rate', 'trimp_score']
    list_filter = ['activity_type', 'start_date', 'upload']
    search_fields = ['activity_type', 'upload__user__username']
    date_hierarchy = 'start_date'
    readonly_fields = ['id']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('upload', 'upload__user')


@admin.register(DailyMetrics)
class DailyMetricsAdmin(admin.ModelAdmin):
    list_display = ['id', 'upload', 'date', 'steps', 'resting_hr', 'total_energy_kcal', 'vo2_max']
    list_filter = ['date', 'upload']
    search_fields = ['upload__user__username']
    date_hierarchy = 'date'
    readonly_fields = ['id']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('upload', 'upload__user')


@admin.register(NightlyMetrics)
class NightlyMetricsAdmin(admin.ModelAdmin):
    list_display = ['id', 'upload', 'date', 'respiratory_rate_mean', 'spo2_median', 'wrist_temp']
    list_filter = ['date', 'upload', 'respiratory_rate_elevated']
    search_fields = ['upload__user__username']
    date_hierarchy = 'date'
    readonly_fields = ['id']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('upload', 'upload__user')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'age', 'gender', 'timezone']
    list_filter = ['gender', 'age']
    search_fields = ['user__username', 'user__email']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
