from django.core.management.base import BaseCommand
from django.db import models
from healthanalytics.models import HealthDataUpload, HealthRecord, Workout
import os
import sys

# Add the src directory to Python path to import exporter functions
from django.conf import settings
src_path = os.path.join(settings.BASE_DIR, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)


class Command(BaseCommand):
    help = 'Quick test of basic Django setup and data models'

    def handle(self, *args, **options):
        self.stdout.write('=== Quick Django Setup Test ===')
        
        try:
            # Test importing exporter
            self.stdout.write('Testing exporter import...')
            from exporter import parse_xml
            self.stdout.write(self.style.SUCCESS('✓ Exporter import successful'))
            
            # Test creating models
            self.stdout.write('Testing model creation...')
            upload = HealthDataUpload.objects.create(processed=False)
            self.stdout.write(f'✓ Created upload: {upload.id}')
            
            # Test creating health record
            from datetime import datetime
            now = datetime.now()
            record = HealthRecord.objects.create(
                upload=upload,
                type='HKQuantityTypeIdentifierStepCount',
                value=1000.0,
                unit='count',
                start_date=now,
                end_date=now,
                creation_date=now
            )
            self.stdout.write(f'✓ Created health record: {record.id}')
            
            # Test creating workout
            workout = Workout.objects.create(
                upload=upload,
                activity_type='HKWorkoutActivityTypeWalking',
                duration=30.0,
                start_date=now,
                end_date=now,
                creation_date=now
            )
            self.stdout.write(f'✓ Created workout: {workout.id}')
            
            # Test queries
            record_count = HealthRecord.objects.count()
            workout_count = Workout.objects.count()
            upload_count = HealthDataUpload.objects.count()
            
            self.stdout.write(f'\n=== Database Counts ===')
            self.stdout.write(f'Uploads: {upload_count}')
            self.stdout.write(f'Health Records: {record_count}')
            self.stdout.write(f'Workouts: {workout_count}')
            
            self.stdout.write(self.style.SUCCESS('\n✓ All basic tests passed!'))
            self.stdout.write('Django setup is working correctly.')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'✗ Test failed: {str(e)}'))
            import traceback
            self.stdout.write(traceback.format_exc())
