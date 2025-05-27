from django.core.management.base import BaseCommand
from django.db import models
from healthanalytics.models import HealthDataUpload, HealthRecord, Workout
from datetime import datetime, timedelta
import random


class Command(BaseCommand):
    help = 'Create sample health data for testing the API'

    def add_arguments(self, parser):
        parser.add_argument(
            '--num-records',
            type=int,
            default=100,
            help='Number of health records to create'
        )
        parser.add_argument(
            '--num-workouts',
            type=int,
            default=10,
            help='Number of workouts to create'
        )

    def handle(self, *args, **options):
        num_records = options['num_records']
        num_workouts = options['num_workouts']
        
        self.stdout.write(f'Creating sample health data...')
        self.stdout.write(f'Records: {num_records}, Workouts: {num_workouts}')
        
        # Create a test upload record
        upload = HealthDataUpload.objects.create(processed=True)
        self.stdout.write(f'Created upload record with ID: {upload.id}')
        
        # Create sample health records
        self.create_sample_records(upload, num_records)
        
        # Create sample workouts
        self.create_sample_workouts(upload, num_workouts)
        
        # Show statistics
        self.show_statistics(upload)
    
    def create_sample_records(self, upload, count):
        """Create sample health records"""
        self.stdout.write(f'Creating {count} sample health records...')
        
        record_types = [
            ('HKQuantityTypeIdentifierStepCount', 'count', 1000, 15000),
            ('HKQuantityTypeIdentifierHeartRate', 'count/min', 60, 180),
            ('HKQuantityTypeIdentifierRestingHeartRate', 'count/min', 45, 80),
            ('HKQuantityTypeIdentifierDistanceWalkingRunning', 'km', 0.5, 10.0),
            ('HKQuantityTypeIdentifierActiveEnergyBurned', 'kcal', 100, 800),
            ('HKQuantityTypeIdentifierBasalEnergyBurned', 'kcal', 1200, 2000),
            ('HKQuantityTypeIdentifierOxygenSaturation', '%', 95, 100),
            ('HKQuantityTypeIdentifierRespiratoryRate', 'count/min', 12, 20),
            ('HKQuantityTypeIdentifierBodyTemperature', '°C', 36.0, 37.5),
        ]
        
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(count):
            record_type, unit, min_val, max_val = random.choice(record_types)
            
            # Create a timestamp within the last 30 days
            days_offset = random.randint(0, 30)
            hours_offset = random.randint(0, 23)
            minutes_offset = random.randint(0, 59)
            
            record_time = base_date + timedelta(
                days=days_offset, 
                hours=hours_offset, 
                minutes=minutes_offset
            )
            
            value = round(random.uniform(min_val, max_val), 2)
            
            HealthRecord.objects.create(
                upload=upload,
                type=record_type,
                value=value,
                unit=unit,
                start_date=record_time,
                end_date=record_time + timedelta(minutes=1),
                creation_date=record_time + timedelta(minutes=2)
            )
        
        self.stdout.write(f'✓ Created {count} health records')
    
    def create_sample_workouts(self, upload, count):
        """Create sample workouts"""
        self.stdout.write(f'Creating {count} sample workouts...')
        
        workout_types = [
            ('HKWorkoutActivityTypeWalking', 15, 90),
            ('HKWorkoutActivityTypeRunning', 20, 120),
            ('HKWorkoutActivityTypeCycling', 30, 180),
            ('HKWorkoutActivityTypeSwimming', 20, 60),
            ('HKWorkoutActivityTypeYoga', 30, 90),
            ('HKWorkoutActivityTypeStrengthTraining', 20, 60),
        ]
        
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(count):
            activity_type, min_duration, max_duration = random.choice(workout_types)
            
            # Create a timestamp within the last 30 days
            days_offset = random.randint(0, 30)
            hours_offset = random.randint(6, 20)  # Workouts during day
            
            start_time = base_date + timedelta(
                days=days_offset, 
                hours=hours_offset
            )
            
            duration = round(random.uniform(min_duration, max_duration), 1)
            end_time = start_time + timedelta(minutes=duration)
            
            # Random heart rate stats
            avg_hr = random.randint(100, 160) if activity_type in ['HKWorkoutActivityTypeRunning', 'HKWorkoutActivityTypeCycling'] else random.randint(80, 120)
            trimp = round(duration * avg_hr * 0.01, 1)
            
            Workout.objects.create(
                upload=upload,
                activity_type=activity_type,
                duration=duration,
                start_date=start_time,
                end_date=end_time,
                creation_date=end_time + timedelta(minutes=5),
                avg_heart_rate=avg_hr,
                trimp_score=trimp
            )
        
        self.stdout.write(f'✓ Created {count} workouts')
    
    def show_statistics(self, upload):
        """Show statistics about the created data"""
        self.stdout.write('\n=== Sample Data Statistics ===')
        
        record_count = upload.records.count()
        workout_count = upload.workouts.count()
        
        self.stdout.write(f'Total Health Records: {record_count}')
        self.stdout.write(f'Total Workouts: {workout_count}')
        
        # Show record types
        if record_count > 0:
            self.stdout.write('\n=== Health Record Types ===')
            record_types = upload.records.values_list('type', flat=True).distinct().order_by('type')
            for record_type in record_types:
                count = upload.records.filter(type=record_type).count()
                self.stdout.write(f'  {record_type}: {count} records')
        
        # Show workout types
        if workout_count > 0:
            self.stdout.write('\n=== Workout Types ===')
            workout_types = upload.workouts.values_list('activity_type', flat=True).distinct().order_by('activity_type')
            for workout_type in workout_types:
                count = upload.workouts.filter(activity_type=workout_type).count()
                total_duration = upload.workouts.filter(activity_type=workout_type).aggregate(
                    total=models.Sum('duration')
                )['total'] or 0
                self.stdout.write(f'  {workout_type}: {count} workouts, {total_duration:.1f} total minutes')
        
        self.stdout.write(f'\nUpload ID: {upload.id}')
        self.stdout.write('\n=== Test API Endpoints ===')
        self.stdout.write(f'All Records: http://127.0.0.1:8000/api/records/?upload={upload.id}')
        self.stdout.write(f'All Workouts: http://127.0.0.1:8000/api/workouts/?upload={upload.id}')
        self.stdout.write(f'Heart Rate Records: http://127.0.0.1:8000/api/records/?upload={upload.id}&type=HKQuantityTypeIdentifierHeartRate')
        self.stdout.write(f'Step Count Records: http://127.0.0.1:8000/api/records/?upload={upload.id}&type=HKQuantityTypeIdentifierStepCount')
        self.stdout.write(f'Running Workouts: http://127.0.0.1:8000/api/workouts/?upload={upload.id}&activity_type=HKWorkoutActivityTypeRunning')
