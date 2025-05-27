"""
Health Analytics Service Module

This module adapts the functions from src/exporter.py for use in Django.
It provides services for processing Apple Health data and computing analytics.
"""

import os
import sys
import pandas as pd
import numpy as np
import tempfile
import zipfile
from typing import Optional, Dict, Any, Tuple
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile

# Add the src directory to Python path to import exporter functions
src_path = os.path.join(settings.BASE_DIR, 'src')
if src_path not in sys.path:
    sys.path.append(src_path)

try:
    from exporter import (
        parse_xml, extract_zip, filter_workout_data, filter_by_date,
        get_heartrate_for_workout, calculate_heartrate_stats,
        nightly_respiratory_rate_stats, nightly_spo2_stats, daily_step_count,
        daily_resting_hr, vo2max_trend, walking_efficiency, daily_hrv,
        nightly_temp_deviation, daily_met_minutes, daily_energy,
        trimp_score, observed_max_hr
    )
except ImportError as e:
    print(f"Warning: Could not import exporter functions: {e}")
    # Define fallback functions if import fails
    def parse_xml(*args, **kwargs):
        raise NotImplementedError("Exporter functions not available")


class HealthDataProcessor:
    """Service class for processing Apple Health data uploads"""
    
    def __init__(self, upload_instance):
        self.upload = upload_instance
        self.data = None
        self.workouts = None
    
    def process_uploaded_file(self) -> Tuple[bool, str]:
        """
        Process an uploaded health data file (ZIP or XML)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            file_path = self.upload.file.path
            
            if file_path.endswith('.zip'):
                return self._process_zip_file(file_path)
            elif file_path.endswith('.xml'):
                return self._process_xml_file(file_path)
            else:
                return False, "Unsupported file format. Please upload a ZIP or XML file."
                
        except Exception as e:
            return False, f"Error processing file: {str(e)}"
    
    def _process_zip_file(self, zip_path: str) -> Tuple[bool, str]:
        """Process a ZIP file containing Apple Health export"""
        try:
            # Create temporary directory for extraction
            with tempfile.TemporaryDirectory() as temp_dir:
                # Extract ZIP file
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    zip_ref.extractall(temp_dir)
                
                # Look for export.xml in the extracted files
                xml_path = None
                for root, dirs, files in os.walk(temp_dir):
                    if 'export.xml' in files:
                        xml_path = os.path.join(root, 'export.xml')
                        break
                
                if not xml_path:
                    return False, "No export.xml found in the ZIP file"
                
                return self._process_xml_file(xml_path)
                
        except Exception as e:
            return False, f"Error extracting ZIP file: {str(e)}"
    
    def _process_xml_file(self, xml_path: str) -> Tuple[bool, str]:
        """Process an XML file containing Apple Health data"""
        try:
            # Parse the XML file using your exporter function
            self.data, self.workouts = parse_xml(xml_path)
            
            # Store data in Django models
            self._save_to_models()
            
            # Compute analytics
            self._compute_analytics()
            
            return True, f"Successfully processed {len(self.data)} health records and {len(self.workouts)} workouts"
            
        except Exception as e:
            return False, f"Error parsing XML file: {str(e)}"
    
    def _save_to_models(self):
        """Save parsed data to Django models"""
        from .models import HealthRecord, Workout
        
        # Clear existing data for this upload
        HealthRecord.objects.filter(upload=self.upload).delete()
        Workout.objects.filter(upload=self.upload).delete()
        
        # Save health records
        health_records = []
        for _, row in self.data.iterrows():
            health_records.append(HealthRecord(
                upload=self.upload,
                type=row['type'],
                value=row['value'],
                unit=row.get('unit', ''),
                start_date=row['startDate'],
                end_date=row['endDate'],
                creation_date=row['creationDate']
            ))
        
        # Batch create for better performance
        HealthRecord.objects.bulk_create(health_records, batch_size=1000)
        
        # Save workouts
        workout_records = []
        for _, row in self.workouts.iterrows():
            workout_records.append(Workout(
                upload=self.upload,
                activity_type=row['workoutActivityType'],
                duration=row['duration'],
                start_date=row['startDate'],
                end_date=row['endDate'],
                creation_date=row['creationDate']
            ))
        
        Workout.objects.bulk_create(workout_records, batch_size=1000)
    
    def _compute_analytics(self):
        """Compute and save analytics using your exporter functions"""
        from .models import DailyMetrics, NightlyMetrics
        
        # Clear existing metrics
        DailyMetrics.objects.filter(upload=self.upload).delete()
        NightlyMetrics.objects.filter(upload=self.upload).delete()
        
        try:
            # Compute daily metrics
            self._compute_daily_metrics()
            
            # Compute nightly metrics
            self._compute_nightly_metrics()
            
        except Exception as e:
            print(f"Warning: Error computing analytics: {e}")
    
    def _compute_daily_metrics(self):
        """Compute daily metrics using your exporter functions"""
        from .models import DailyMetrics
        
        try:
            # Step count metrics
            step_stats = daily_step_count(self.data)
            
            # Energy metrics
            energy_stats = daily_energy(self.data)
            
            # Resting heart rate
            resting_hr_stats = daily_resting_hr(self.data)
            
            # HRV metrics
            hrv_stats = daily_hrv(self.data)
            
            # VO2 max
            vo2_stats = vo2max_trend(self.data)
            
            # MET minutes
            met_stats = daily_met_minutes(self.data)
            
            # Combine all metrics by date
            all_dates = set()
            for stats in [step_stats, energy_stats, resting_hr_stats, hrv_stats, vo2_stats, met_stats]:
                if hasattr(stats, 'index'):
                    all_dates.update(stats.index)
            
            daily_metrics = []
            for date in all_dates:
                metric = DailyMetrics(
                    upload=self.upload,
                    date=date,
                    steps=step_stats.get('steps', {}).get(date) if hasattr(step_stats, 'get') else None,
                    steps_7day_avg=step_stats.get('rolling7', {}).get(date) if hasattr(step_stats, 'get') else None,
                    step_streak=step_stats.get('streak', {}).get(date) if hasattr(step_stats, 'get') else None,
                    resting_hr=resting_hr_stats.get(date) if hasattr(resting_hr_stats, 'get') else None,
                    basal_energy_kcal=energy_stats.get('basal_kcal', {}).get(date) if hasattr(energy_stats, 'get') else None,
                    active_energy_kcal=energy_stats.get('active_kcal', {}).get(date) if hasattr(energy_stats, 'get') else None,
                    total_energy_kcal=energy_stats.get('total_kcal', {}).get(date) if hasattr(energy_stats, 'get') else None,
                    hrv_sdnn=hrv_stats.get('sdnn', {}).get(date) if hasattr(hrv_stats, 'get') else None,
                    hrv_baseline=hrv_stats.get('baseline7', {}).get(date) if hasattr(hrv_stats, 'get') else None,
                    hrv_z_score=hrv_stats.get('z_score', {}).get(date) if hasattr(hrv_stats, 'get') else None,
                    vo2_max=vo2_stats.get(date) if hasattr(vo2_stats, 'get') else None,
                    met_minutes=met_stats.get(date) if hasattr(met_stats, 'get') else None,
                )
                daily_metrics.append(metric)
            
            DailyMetrics.objects.bulk_create(daily_metrics, batch_size=1000)
            
        except Exception as e:
            print(f"Error computing daily metrics: {e}")
    
    def _compute_nightly_metrics(self):
        """Compute nightly metrics using your exporter functions"""
        from .models import NightlyMetrics
        
        try:
            # Respiratory rate metrics
            rr_stats = nightly_respiratory_rate_stats(self.data)
            
            # SpO2 metrics
            spo2_stats = nightly_spo2_stats(self.data)
            
            # Temperature metrics
            temp_stats = nightly_temp_deviation(self.data)
            
            # Combine metrics by date
            all_dates = set()
            for stats in [rr_stats, spo2_stats, temp_stats]:
                if hasattr(stats, 'index'):
                    all_dates.update(stats.index)
            
            nightly_metrics = []
            for date in all_dates:
                metric = NightlyMetrics(
                    upload=self.upload,
                    date=date,
                    respiratory_rate_mean=rr_stats.get('RR_mean', {}).get(date) if hasattr(rr_stats, 'get') else None,
                    respiratory_rate_baseline=rr_stats.get('RR_baseline', {}).get(date) if hasattr(rr_stats, 'get') else None,
                    respiratory_rate_z_score=rr_stats.get('RR_z', {}).get(date) if hasattr(rr_stats, 'get') else None,
                    respiratory_rate_elevated=rr_stats.get('elevated', {}).get(date, False) if hasattr(rr_stats, 'get') else False,
                    spo2_median=spo2_stats.get('SpO2_median', {}).get(date) if hasattr(spo2_stats, 'get') else None,
                    spo2_p01=spo2_stats.get('SpO2_p01', {}).get(date) if hasattr(spo2_stats, 'get') else None,
                    pct_time_below_90=spo2_stats.get('pct_time_below_90', {}).get(date) if hasattr(spo2_stats, 'get') else None,
                    wrist_temp=temp_stats.get('wrist_temp', {}).get(date) if hasattr(temp_stats, 'get') else None,
                    temp_baseline=temp_stats.get('baseline', {}).get(date) if hasattr(temp_stats, 'get') else None,
                    temp_deviation=temp_stats.get('delta', {}).get(date) if hasattr(temp_stats, 'get') else None,
                )
                nightly_metrics.append(metric)
            
            NightlyMetrics.objects.bulk_create(nightly_metrics, batch_size=1000)
            
        except Exception as e:
            print(f"Error computing nightly metrics: {e}")


class HealthAnalyticsService:
    """Service class for retrieving and computing health analytics"""
    
    @staticmethod
    def get_workout_heart_rate_analysis(workout_id: int, user_age: Optional[int] = None) -> Dict[str, Any]:
        """
        Get detailed heart rate analysis for a specific workout
        
        Args:
            workout_id: ID of the workout to analyze
            user_age: Age of the user for heart rate zone calculations
            
        Returns:
            Dictionary containing heart rate statistics
        """
        from .models import Workout, HealthRecord
        
        try:
            workout = Workout.objects.get(id=workout_id)
            
            # Get heart rate data for the workout period
            hr_records = HealthRecord.objects.filter(
                upload=workout.upload,
                type='HeartRate',
                start_date__gte=workout.start_date,
                end_date__lte=workout.end_date
            )
            
            if not hr_records.exists():
                return {"error": "No heart rate data found for this workout"}
            
            # Convert to DataFrame for analysis
            hr_data = pd.DataFrame([{
                'value': record.value,
                'startDate': record.start_date,
                'endDate': record.end_date
            } for record in hr_records])
            
            # Use your exporter function to calculate stats
            stats = calculate_heartrate_stats(hr_data, age=user_age)
            
            return stats
            
        except Workout.DoesNotExist:
            return {"error": "Workout not found"}
        except Exception as e:
            return {"error": f"Error analyzing heart rate: {str(e)}"}
    
    @staticmethod
    def calculate_trimp_for_workout(workout_id: int, user_gender: str = 'male') -> Optional[float]:
        """
        Calculate TRIMP score for a specific workout
        
        Args:
            workout_id: ID of the workout
            user_gender: Gender for TRIMP calculation
            
        Returns:
            TRIMP score or None if calculation fails
        """
        from .models import Workout, HealthRecord, DailyMetrics
        
        try:
            workout = Workout.objects.get(id=workout_id)
            
            # Get average heart rate for the workout
            hr_stats = HealthAnalyticsService.get_workout_heart_rate_analysis(workout_id)
            if 'error' in hr_stats or not hr_stats.get('avg_hr'):
                return None
            
            # Get resting heart rate for the workout date
            workout_date = workout.start_date.date()
            daily_metric = DailyMetrics.objects.filter(
                upload=workout.upload,
                date=workout_date
            ).first()
            
            if not daily_metric or not daily_metric.resting_hr:
                # Fallback: get resting HR from nearby dates
                nearby_metrics = DailyMetrics.objects.filter(
                    upload=workout.upload,
                    resting_hr__isnull=False
                ).order_by('-date')[:7]
                
                if nearby_metrics:
                    hr_rest = sum(m.resting_hr for m in nearby_metrics) / len(nearby_metrics)
                else:
                    hr_rest = 60.0  # Default fallback
            else:
                hr_rest = daily_metric.resting_hr
            
            # Get max heart rate from all user's data
            max_hr_record = HealthRecord.objects.filter(
                upload=workout.upload,
                type='HeartRate'
            ).aggregate(max_hr=models.Max('value'))
            
            hr_max = max_hr_record['max_hr'] or 190.0  # Default fallback
            
            # Calculate TRIMP score
            trimp = trimp_score(
                duration_min=workout.duration,
                hr_avg=hr_stats['avg_hr'],
                hr_rest=hr_rest,
                hr_max=hr_max,
                gender=user_gender
            )
            
            # Update the workout with calculated TRIMP
            workout.trimp_score = trimp
            workout.avg_heart_rate = hr_stats['avg_hr']
            workout.save()
            
            return trimp
            
        except Exception as e:
            print(f"Error calculating TRIMP: {e}")
            return None
