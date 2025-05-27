from django.core.management.base import BaseCommand
from django.db import models
from healthanalytics.models import HealthDataUpload
import os
import xml.etree.ElementTree as ET
import tempfile


class Command(BaseCommand):
    help = 'Process a subset of Apple Health data for testing'

    def add_arguments(self, parser):
        parser.add_argument(
            '--xml-path',
            type=str,
            default='src/data/apple_health_export/export.xml',
            help='Path to Apple Health export.xml file'
        )
        parser.add_argument(
            '--max-records',
            type=int,
            default=1000,
            help='Maximum number of records to process'
        )

    def handle(self, *args, **options):
        xml_path = options['xml_path']
        max_records = options['max_records']
        
        # Check if the file exists
        if not os.path.exists(xml_path):
            self.stdout.write(
                self.style.ERROR(f'File not found: {xml_path}')
            )
            return
        
        self.stdout.write(f'Processing subset of Apple Health data from: {xml_path}')
        self.stdout.write(f'Max records to process: {max_records}')
        
        # Create a temporary XML file with subset of data
        temp_xml_path = self.create_subset_xml(xml_path, max_records)
        
        try:
            # Create a test upload record
            upload = HealthDataUpload.objects.create(processed=False)
            self.stdout.write(f'Created upload record with ID: {upload.id}')
            
            # Process the subset data
            processor = HealthDataProcessor(upload)
            
            self.stdout.write('Starting XML processing...')
            success, message = processor._process_xml_file(temp_xml_path)
            
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
            import traceback
            self.stdout.write(traceback.format_exc())
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_xml_path):
                os.remove(temp_xml_path)
    
    def create_subset_xml(self, xml_path, max_records):
        """Create a temporary XML file with a subset of records"""
        self.stdout.write(f'Creating subset XML with max {max_records} records...')
        
        temp_fd, temp_path = tempfile.mkstemp(suffix='.xml')
        
        try:
            with os.fdopen(temp_fd, 'w', encoding='utf-8') as temp_file:
                temp_file.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                temp_file.write('<!DOCTYPE HealthData [\n')
                temp_file.write('<!ELEMENT HealthData (ExportDate,Me,(Record|Workout|ActivitySummary|ClinicalRecord)*)>\n')
                temp_file.write('<!ATTLIST HealthData locale CDATA #REQUIRED>\n')
                temp_file.write('<!ELEMENT ExportDate (#PCDATA)>\n')
                temp_file.write('<!ATTLIST ExportDate value CDATA #REQUIRED>\n')
                temp_file.write(']>\n')
                temp_file.write('<HealthData locale="en_US">\n')
                temp_file.write('<ExportDate value="2025-05-27 15:00:00 -0700"/>\n')
                temp_file.write('<Me HKCharacteristicTypeIdentifierDateOfBirth="1990-01-01"/>\n')
                
                # Parse the original XML and copy a subset of records
                record_count = 0
                workout_count = 0
                
                # Use iterparse to handle large files efficiently
                for event, elem in ET.iterparse(xml_path, events=('start', 'end')):
                    if event == 'end':
                        if elem.tag == 'Record' and record_count < max_records:
                            # Write the record element
                            temp_file.write(ET.tostring(elem, encoding='unicode'))
                            temp_file.write('\n')
                            record_count += 1
                        elif elem.tag == 'Workout' and workout_count < max_records // 10:
                            # Include some workouts (fewer than records)
                            temp_file.write(ET.tostring(elem, encoding='unicode'))
                            temp_file.write('\n')
                            workout_count += 1
                        
                        # Clear the element to save memory
                        elem.clear()
                        
                        if record_count >= max_records and workout_count >= max_records // 10:
                            break
                
                temp_file.write('</HealthData>\n')
                
                self.stdout.write(f'Created subset XML with {record_count} records and {workout_count} workouts')
                
        except Exception as e:
            os.close(temp_fd)
            raise e
            
        return temp_path
    
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
            self.stdout.write('\n=== Health Record Types (Top 10) ===')
            record_types = upload.records.values_list('type', flat=True).distinct().order_by('type')
            for record_type in record_types[:10]:
                count = upload.records.filter(type=record_type).count()
                self.stdout.write(f'  {record_type}: {count} records')
        
        # Show workout types
        if workout_count > 0:
            self.stdout.write('\n=== Workout Types ===')
            workout_types = upload.workouts.values_list('activity_type', flat=True).distinct().order_by('activity_type')
            for workout_type in workout_types:
                count = upload.workouts.filter(activity_type=workout_type).count()
                self.stdout.write(f'  {workout_type}: {count} workouts')
        
        self.stdout.write(f'\nUpload ID: {upload.id}')
        self.stdout.write('You can now test the API endpoints with this upload ID!')
        self.stdout.write(f'API URLs:')
        self.stdout.write(f'  Records: http://127.0.0.1:8000/api/records/?upload={upload.id}')
        self.stdout.write(f'  Workouts: http://127.0.0.1:8000/api/workouts/?upload={upload.id}')
