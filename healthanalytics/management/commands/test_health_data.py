from django.core.management.base import BaseCommand
from django.core.files import File
from django.db import models
from healthanalytics.models import HealthDataUpload
from healthanalytics.services import HealthDataProcessor
import os


class Command(BaseCommand):
    help = 'Test health data processing with existing Apple Health export'

    def add_arguments(self, parser):
        parser.add_argument(
            '--xml-path',
            type=str,
            default='src/data/apple_health_export/export.xml',
            help='Path to Apple Health export.xml file'
        )

    def handle(self, *args, **options):
        xml_path = options['xml_path']
        
        # Check if the file exists
        if not os.path.exists(xml_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {xml_path}')
            )
            return
        
        self.stdout.write(f'Processing Apple Health data from: {xml_path}')
        self.stdout.write('Creating upload record...')
        
        # Create a test upload record
        upload = HealthDataUpload.objects.create(
            processed=False
        )
        self.stdout.write(f'Created upload record with ID: {upload.id}')
        
        # Manually set the file path (since we're not actually uploading)
        upload.file.name = xml_path
        upload.save()
        
        # Process the data
        processor = HealthDataProcessor(upload)
        self.stdout.write('Starting XML processing... (this may take a while for large files)')
        
        try:
            # Directly process the XML file
            success, message = processor._process_xml_file(xml_path)
            
            if success:
                upload.processed = True
                upload.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully processed: {message}')
                )
                
                # Show some statistics
                self.show_statistics(upload)
                
            else:
                upload.processing_error = message
                upload.save()
                self.stdout.write(
                    self.style.ERROR(f'Processing failed: {message}')
                )
                
        except Exception as e:
            upload.processing_error = str(e)
            upload.save()
            self.stdout.write(
                self.style.ERROR(f'Error during processing: {str(e)}')
            )
    
    def show_statistics(self, upload):
        """Show statistics about the processed data"""
        self.stdout.write('\n=== Health Data Statistics ===')
        
        # Record counts by type
        from healthanalytics.models import HealthRecord, Workout, DailyMetrics, NightlyMetrics
        
        record_count = upload.records.count()
        workout_count = upload.workouts.count()
        daily_metrics_count = upload.daily_metrics.count()
        nightly_metrics_count = upload.nightly_metrics.count()
        
        self.stdout.write(f'Total Health Records: {record_count}')
        self.stdout.write(f'Total Workouts: {workout_count}')
        self.stdout.write(f'Daily Metrics: {daily_metrics_count}')
        self.stdout.write(f'Nightly Metrics: {nightly_metrics_count}')
        
        # Show record types
        if record_count > 0:
            self.stdout.write('\n=== Available Health Record Types ===')
            record_types = upload.records.values_list('type', flat=True).distinct().order_by('type')
            for record_type in record_types[:20]:  # Show first 20 types
                count = upload.records.filter(type=record_type).count()
                self.stdout.write(f'  {record_type}: {count} records')
            
            if record_types.count() > 20:
                self.stdout.write(f'  ... and {record_types.count() - 20} more types')
        
        # Show workout types
        if workout_count > 0:
            self.stdout.write('\n=== Available Workout Types ===')
            workout_types = upload.workouts.values_list('activity_type', flat=True).distinct().order_by('activity_type')
            for workout_type in workout_types:
                count = upload.workouts.filter(activity_type=workout_type).count()
                total_duration = upload.workouts.filter(activity_type=workout_type).aggregate(
                    total=models.Sum('duration')
                )['total'] or 0
                self.stdout.write(f'  {workout_type}: {count} workouts, {total_duration:.1f} total minutes')
        
        # Show sample daily metrics
        if daily_metrics_count > 0:
            self.stdout.write('\n=== Sample Daily Metrics (Last 5 Days) ===')
            recent_metrics = upload.daily_metrics.order_by('-date')[:5]
            for metric in recent_metrics:
                self.stdout.write(
                    f'  {metric.date}: Steps={metric.steps}, '
                    f'Resting HR={metric.resting_hr}, '
                    f'Energy={metric.total_energy_kcal}kcal'
                )
        
        # Show sample nightly metrics
        if nightly_metrics_count > 0:
            self.stdout.write('\n=== Sample Nightly Metrics (Last 5 Nights) ===')
            recent_metrics = upload.nightly_metrics.order_by('-date')[:5]
            for metric in recent_metrics:
                self.stdout.write(
                    f'  {metric.date}: RR={metric.respiratory_rate_mean}, '
                    f'SpO2={metric.spo2_median}%, '
                    f'Temp={metric.wrist_temp}°C'
                )
        
        self.stdout.write(f'\nUpload ID: {upload.id}')
        self.stdout.write('You can now test the API endpoints with this upload ID!')
