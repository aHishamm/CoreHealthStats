import os
import unittest
import pandas as pd
import numpy as np
import datetime as dt
from pandas._testing import assert_frame_equal, assert_series_equal
import xml.etree.ElementTree as ET
from io import StringIO
import tempfile
import zipfile
import shutil

# Import the module to test
import exporter

class TestExporter(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Create sample health data for testing
        self.sample_data = pd.DataFrame({
            'type': ['HeartRate', 'HeartRate', 'StepCount', 'StepCount', 'RestingHeartRate', 
                    'RespiratoryRate', 'OxygenSaturation', 'VO2Max', 'WalkingHeartRateAverage',
                    'WalkingSpeed', 'HeartRateVariabilitySDNN', 'AppleSleepingWristTemperature',
                    'PhysicalEffort', 'BasalEnergyBurned', 'ActiveEnergyBurned'],
            'startDate': [
                pd.Timestamp('2024-01-01 08:00:00'),
                pd.Timestamp('2024-01-01 09:00:00'),
                pd.Timestamp('2024-01-01 08:00:00'),
                pd.Timestamp('2024-01-02 08:00:00'),
                pd.Timestamp('2024-01-01 08:00:00'),
                pd.Timestamp('2024-01-01 23:00:00'),
                pd.Timestamp('2024-01-01 23:00:00'),
                pd.Timestamp('2024-01-01 08:00:00'),
                pd.Timestamp('2024-01-01 08:30:00'),
                pd.Timestamp('2024-01-01 08:30:00'),
                pd.Timestamp('2024-01-01 23:00:00'),
                pd.Timestamp('2024-01-01 23:00:00'),
                pd.Timestamp('2024-01-01 08:30:00'),
                pd.Timestamp('2024-01-01 08:00:00'),
                pd.Timestamp('2024-01-01 09:00:00')
            ],
            'endDate': [
                pd.Timestamp('2024-01-01 08:01:00'),
                pd.Timestamp('2024-01-01 09:01:00'),
                pd.Timestamp('2024-01-01 08:01:00'),
                pd.Timestamp('2024-01-02 08:01:00'),
                pd.Timestamp('2024-01-01 08:01:00'),
                pd.Timestamp('2024-01-01 23:30:00'),
                pd.Timestamp('2024-01-01 23:30:00'),
                pd.Timestamp('2024-01-01 08:30:00'),
                pd.Timestamp('2024-01-01 09:00:00'),
                pd.Timestamp('2024-01-01 09:00:00'),
                pd.Timestamp('2024-01-01 23:30:00'),
                pd.Timestamp('2024-01-01 23:30:00'),
                pd.Timestamp('2024-01-01 09:30:00'),
                pd.Timestamp('2024-01-01 08:30:00'),
                pd.Timestamp('2024-01-01 09:30:00')
            ],
            'creationDate': [
                pd.Timestamp('2024-01-01 08:01:00'),
                pd.Timestamp('2024-01-01 09:01:00'),
                pd.Timestamp('2024-01-01 08:01:00'),
                pd.Timestamp('2024-01-02 08:01:00'),
                pd.Timestamp('2024-01-01 08:01:00'),
                pd.Timestamp('2024-01-01 23:30:00'),
                pd.Timestamp('2024-01-01 23:30:00'),
                pd.Timestamp('2024-01-01 08:30:00'),
                pd.Timestamp('2024-01-01 09:00:00'),
                pd.Timestamp('2024-01-01 09:00:00'),
                pd.Timestamp('2024-01-01 23:30:00'),
                pd.Timestamp('2024-01-01 23:30:00'),
                pd.Timestamp('2024-01-01 09:30:00'),
                pd.Timestamp('2024-01-01 08:30:00'),
                pd.Timestamp('2024-01-01 09:30:00')
            ],
            'value': [70.0, 80.0, 1000.0, 1500.0, 65.0, 16.0, 98.0, 40.0, 75.0, 1.5, 50.0, 36.8, 10.0, 1500.0, 500.0],
            'unit': ['count/min', 'count/min', 'count', 'count', 'count/min', 'count/min', '%', 'mL/kg/min', 
                    'count/min', 'm/s', 'ms', 'degC', 'MET', 'kcal', 'kcal']
        })
        
        # Create sample workout data for testing
        self.sample_workouts = pd.DataFrame({
            'workoutActivityType': ['Running', 'Walking', 'Running'],
            'startDate': [
                pd.Timestamp('2024-01-01 08:00:00'),
                pd.Timestamp('2024-01-01 09:00:00'),
                pd.Timestamp('2024-01-02 08:00:00')
            ],
            'endDate': [
                pd.Timestamp('2024-01-01 08:30:00'),
                pd.Timestamp('2024-01-01 09:30:00'),
                pd.Timestamp('2024-01-02 09:00:00')
            ],
            'creationDate': [
                pd.Timestamp('2024-01-01 08:30:00'),
                pd.Timestamp('2024-01-01 09:30:00'),
                pd.Timestamp('2024-01-02 09:00:00')
            ],
            'duration': [30.0, 30.0, 60.0]  # Duration in minutes
        })
        
        # Create a test directory for file operations
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Tear down test fixtures."""
        # Clean up the test directory
        shutil.rmtree(self.test_dir)

    def test_extract_zip(self):
        """Test the extract_zip function."""
        # Create a temporary zip file with test content
        zip_path = os.path.join(self.test_dir, 'test_export.zip')
        
        with zipfile.ZipFile(zip_path, 'w') as zip_ref:
            zip_ref.writestr('test.txt', 'Test content')
        
        # Monkeypatch the __file__ attribute to control extract location
        original_file = exporter.__file__
        try:
            exporter.__file__ = os.path.join(self.test_dir, 'exporter.py')
            
            # Call the function to extract
            exporter.extract_zip(zip_path)
            
            # Check if the file was extracted
            extracted_file = os.path.join(self.test_dir, 'data', 'test.txt')
            self.assertTrue(os.path.exists(extracted_file))
            
            with open(extracted_file, 'r') as f:
                self.assertEqual(f.read(), 'Test content')
        finally:
            exporter.__file__ = original_file

    def test_filter_workout_data(self):
        """Test filtering workout data by workout type."""
        # Filter for 'Running' workouts
        filtered = exporter.filter_workout_data(self.sample_workouts, 'Running')
        
        # Check that only Running workouts are returned
        self.assertEqual(len(filtered), 2)
        self.assertTrue(all(filtered['workoutActivityType'] == 'Running'))
        
        # Test with non-existent workout type
        empty_filtered = exporter.filter_workout_data(self.sample_workouts, 'Swimming')
        self.assertTrue(empty_filtered.empty)

    def test_filter_by_date(self):
        """Test filtering data by date range."""
        start_date = pd.Timestamp('2024-01-01 00:00:00')
        end_date = pd.Timestamp('2024-01-01 23:59:59')
        
        # Filter workouts
        filtered_workouts = exporter.filter_by_date(self.sample_workouts, start_date, end_date)
        
        # Check that only workouts within date range are returned
        self.assertEqual(len(filtered_workouts), 2)
        self.assertTrue(all(filtered_workouts['creationDate'].dt.date == pd.Timestamp('2024-01-01').date()))
        
        # Filter health data
        filtered_data = exporter.filter_by_date(self.sample_data, start_date, end_date)
        expected_count = len(self.sample_data[self.sample_data['creationDate'].dt.date == pd.Timestamp('2024-01-01').date()])
        self.assertEqual(len(filtered_data), expected_count)

    def test_get_heartrate_for_workout(self):
        """Test getting heart rate measurements for a specific workout."""
        # Get heart rate data
        hr_data = self.sample_data[self.sample_data['type'] == 'HeartRate']
        
        # Get a single workout
        workout = self.sample_workouts.iloc[[0]]  # First running workout
        
        # Get heart rate for workout
        hr_for_workout = exporter.get_heartrate_for_workout(hr_data, workout)
        
        # Check that we get heart rate data during the workout time
        self.assertEqual(len(hr_for_workout), 1)  # Should have one HR measurement
        self.assertEqual(hr_for_workout['value'].iloc[0], 70.0)  # First HR value

    def test_calculate_heartrate_stats(self):
        """Test calculating heart rate statistics."""
        # Create sample heart rate data
        hr_data = pd.DataFrame({
            'type': ['HeartRate', 'HeartRate', 'HeartRate', 'HeartRate'],
            'value': [60.0, 70.0, 150.0, 180.0],
            'startDate': [
                pd.Timestamp('2024-01-01 08:00:00'),
                pd.Timestamp('2024-01-01 08:05:00'),
                pd.Timestamp('2024-01-01 08:10:00'),
                pd.Timestamp('2024-01-01 08:15:00')
            ],
            'endDate': [
                pd.Timestamp('2024-01-01 08:01:00'),
                pd.Timestamp('2024-01-01 08:06:00'),
                pd.Timestamp('2024-01-01 08:11:00'),
                pd.Timestamp('2024-01-01 08:16:00')
            ]
        })
        
        # Calculate stats without age
        stats = exporter.calculate_heartrate_stats(hr_data)
        
        # Check min, max, avg
        self.assertEqual(stats['min_hr'], 60.0)
        self.assertEqual(stats['max_hr'], 180.0)
        self.assertEqual(stats['avg_hr'], 115.0)
        
        # Calculate stats with age
        stats_with_age = exporter.calculate_heartrate_stats(hr_data, 30)
        
        # Check estimated max HR (220 - age)
        self.assertEqual(stats_with_age['estimated_max_hr'], 190)
        
        # Test with empty data
        empty_stats = exporter.calculate_heartrate_stats(pd.DataFrame())
        self.assertIsNone(empty_stats['min_hr'])
        self.assertEqual(empty_stats['hr_zones']['resting'], 0)

    def test_nightly_respiratory_rate_stats(self):
        """Test calculating nightly respiratory rate statistics."""
        # Get respiratory rate data
        rr_stats = exporter.nightly_respiratory_rate_stats(self.sample_data)
        
        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(rr_stats, pd.DataFrame)
        for col in ['RR_mean', 'RR_baseline', 'RR_z', 'elevated']:
            self.assertIn(col, rr_stats.columns)
        
        # Value check (limited due to rolling calculations)
        self.assertEqual(rr_stats['RR_mean'].iloc[0], 16.0)

    def test_nightly_spo2_stats(self):
        """Test calculating nightly SPO2 statistics."""
        # Get SPO2 stats
        spo2_stats = exporter.nightly_spo2_stats(self.sample_data)
        
        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(spo2_stats, pd.DataFrame)
        self.assertIn('SpO2_median', spo2_stats.columns)
        self.assertIn('SpO2_p01', spo2_stats.columns)
        self.assertIn('pct_time_below_90', spo2_stats.columns)
        
        # Value check
        self.assertEqual(spo2_stats['SpO2_median'].iloc[0], 98.0)
        self.assertEqual(spo2_stats['pct_time_below_90'].iloc[0], 0.0)  # 98% > 90%

    def test_daily_step_count(self):
        """Test calculating daily step count statistics."""
        # Get step count stats
        step_stats = exporter.daily_step_count(self.sample_data)
        
        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(step_stats, pd.DataFrame)
        self.assertIn('steps', step_stats.columns)
        self.assertIn('rolling7', step_stats.columns)
        self.assertIn('streak', step_stats.columns)
        
        # Value check
        self.assertEqual(step_stats['steps'].iloc[0], 1000.0)  # First day
        self.assertEqual(step_stats['steps'].iloc[1], 1500.0)  # Second day

    def test_vo2max_trend(self):
        """Test extracting VO2 max trend."""
        # Get VO2 max trend
        vo2_trend = exporter.vo2max_trend(self.sample_data)
        
        # Check that the result is a Series
        self.assertIsInstance(vo2_trend, pd.Series)
        
        # Value check
        self.assertEqual(vo2_trend.iloc[0], 40.0)

    def test_walking_efficiency(self):
        """Test calculating walking efficiency."""
        # Get walking efficiency
        walking_eff = exporter.walking_efficiency(self.sample_data)
        
        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(walking_eff, pd.DataFrame)
        self.assertIn('whr_avg', walking_eff.columns)
        self.assertIn('walk_speed', walking_eff.columns)
        self.assertIn('hr_speed_ratio', walking_eff.columns)
        
        # Value check
        self.assertEqual(walking_eff['whr_avg'].iloc[0], 75.0)
        self.assertEqual(walking_eff['walk_speed'].iloc[0], 1.5)
        self.assertEqual(walking_eff['hr_speed_ratio'].iloc[0], 75.0 / 1.5)

    def test_daily_hrv(self):
        """Test calculating daily heart rate variability."""
        # Get daily HRV
        hrv_stats = exporter.daily_hrv(self.sample_data)
        
        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(hrv_stats, pd.DataFrame)
        self.assertIn('sdnn', hrv_stats.columns)
        self.assertIn('baseline7', hrv_stats.columns)
        self.assertIn('z_score', hrv_stats.columns)
        
        # Value check
        self.assertEqual(hrv_stats['sdnn'].iloc[0], 50.0)

    def test_nightly_temp_deviation(self):
        """Test calculating nightly temperature deviation."""
        # Get nightly temperature deviation
        temp_stats = exporter.nightly_temp_deviation(self.sample_data)
        
        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(temp_stats, pd.DataFrame)
        self.assertIn('wrist_temp', temp_stats.columns)
        self.assertIn('baseline', temp_stats.columns)
        self.assertIn('delta', temp_stats.columns)
        
        # Value check
        self.assertEqual(temp_stats['wrist_temp'].iloc[0], 36.8)

    def test_daily_met_minutes(self):
        """Test calculating daily MET minutes."""
        # Get daily MET minutes
        met_minutes = exporter.daily_met_minutes(self.sample_data)
        
        # Check that the result is a Series
        self.assertIsInstance(met_minutes, pd.Series)
        
        # Value check
        self.assertEqual(met_minutes.iloc[0], 10.0)

    def test_daily_energy(self):
        """Test calculating daily energy expenditure."""
        # Get daily energy
        energy_stats = exporter.daily_energy(self.sample_data)
        
        # Check that the result is a DataFrame with expected columns
        self.assertIsInstance(energy_stats, pd.DataFrame)
        self.assertIn('basal_kcal', energy_stats.columns)
        self.assertIn('active_kcal', energy_stats.columns)
        self.assertIn('total_kcal', energy_stats.columns)
        
        # Value check
        self.assertEqual(energy_stats['basal_kcal'].iloc[0], 1500.0)
        self.assertEqual(energy_stats['active_kcal'].iloc[0], 500.0)
        self.assertEqual(energy_stats['total_kcal'].iloc[0], 2000.0)

    def test_daily_resting_hr(self):
        """Test calculating daily resting heart rate."""
        # Get daily resting HR
        resting_hr = exporter.daily_resting_hr(self.sample_data)
        
        # Check that the result is a Series
        self.assertIsInstance(resting_hr, pd.Series)
        
        # Value check
        self.assertEqual(resting_hr.iloc[0], 65.0)

    def test_observed_max_hr(self):
        """Test getting the observed maximum heart rate."""
        # Get observed max HR
        max_hr = exporter.observed_max_hr(self.sample_data)
        
        # Check result
        self.assertEqual(max_hr, 80)

    def test_trimp_score(self):
        """Test calculating TRIMP score."""
        # Calculate TRIMP score
        trimp = exporter.trimp_score(
            duration_min=30.0,
            hr_avg=150.0,
            hr_rest=60.0,
            hr_max=190.0,
            gender="male"
        )
        
        # Check that result is a float > 0
        self.assertIsInstance(trimp, float)
        self.assertGreater(trimp, 0)
        
        # Edge case: delta <= 0
        edge_trimp = exporter.trimp_score(
            duration_min=30.0,
            hr_avg=50.0,  # HR average below resting
            hr_rest=60.0,
            hr_max=190.0,
            gender="male"
        )
        self.assertEqual(edge_trimp, 0.0)
        
        # Test female calculation (different coefficient)
        female_trimp = exporter.trimp_score(
            duration_min=30.0,
            hr_avg=150.0,
            hr_rest=60.0,
            hr_max=190.0,
            gender="female"
        )
        self.assertIsInstance(female_trimp, float)
        self.assertNotEqual(trimp, female_trimp)  # Should be different from male

    def test_add_trimp_column(self):
        """Test adding TRIMP column to workout data."""
        # Create a sample dataset for this specific test
        hr_data = pd.DataFrame({
            'type': ['HeartRate', 'HeartRate', 'RestingHeartRate'],
            'value': [120.0, 150.0, 65.0],
            'startDate': [
                pd.Timestamp('2024-01-01 08:05:00'),
                pd.Timestamp('2024-01-01 08:15:00'),
                pd.Timestamp('2024-01-01 06:00:00')
            ],
            'endDate': [
                pd.Timestamp('2024-01-01 08:10:00'),
                pd.Timestamp('2024-01-01 08:20:00'),
                pd.Timestamp('2024-01-01 06:05:00')
            ],
            'creationDate': [
                pd.Timestamp('2024-01-01 08:10:00'),
                pd.Timestamp('2024-01-01 08:20:00'),
                pd.Timestamp('2024-01-01 06:05:00')
            ]
        })
        
        workout = pd.DataFrame({
            'workoutActivityType': ['Running'],
            'startDate': [pd.Timestamp('2024-01-01 08:00:00')],
            'endDate': [pd.Timestamp('2024-01-01 08:30:00')],
            'duration': [30.0]  # Duration in minutes
        })
        
        # Add TRIMP column
        workout_with_trimp = exporter.add_trimp_column(workout, hr_data)
        
        # Check that the result has the expected columns
        self.assertIn('avg_hr', workout_with_trimp.columns)
        self.assertIn('TRIMP', workout_with_trimp.columns)
        
        # Check that the TRIMP value is a float
        self.assertIsInstance(workout_with_trimp['TRIMP'].iloc[0], float)

    def create_mock_xml(self):
        """Create a temporary XML file for testing parse_xml function."""
        xml_content = """
        <HealthData>
            <Record type="HKQuantityTypeIdentifierHeartRate" startDate="2024-01-01 08:00:00" endDate="2024-01-01 08:01:00" value="70" unit="count/min" creationDate="2024-01-01 08:01:00" />
            <Record type="HKQuantityTypeIdentifierStepCount" startDate="2024-01-01 08:00:00" endDate="2024-01-01 08:01:00" value="10" unit="count" creationDate="2024-01-01 08:01:00" />
            <Workout workoutActivityType="HKWorkoutActivityTypeRunning" startDate="2024-01-01 08:00:00" endDate="2024-01-01 08:30:00" duration="30" creationDate="2024-01-01 08:30:00" />
        </HealthData>
        """
        xml_path = os.path.join(self.test_dir, 'test_export.xml')
        with open(xml_path, 'w') as f:
            f.write(xml_content)
        return xml_path

    def test_parse_xml(self):
        """Test parsing XML health export file."""
        xml_path = self.create_mock_xml()
        
        # Test parse_xml with default settings
        data, workout_data = exporter.parse_xml(xml_path)
        
        # Check record data
        self.assertEqual(len(data), 2)
        self.assertIn('HeartRate', data['type'].values)
        self.assertIn('StepCount', data['type'].values)
        
        # Check workout data
        self.assertEqual(len(workout_data), 1)
        self.assertEqual(workout_data['workoutActivityType'].iloc[0], 'Running')
        self.assertEqual(workout_data['duration'].iloc[0], 30.0)
        
        # Test with save options (only testing that it doesn't crash)
        export_dir = os.path.join(self.test_dir, 'export')
        os.makedirs(export_dir, exist_ok=True)
        
        # Mock the save path
        original_cwd = os.getcwd()
        try:
            os.chdir(self.test_dir)
            data, workout_data = exporter.parse_xml(xml_path, save_to_csv=True)
        finally:
            os.chdir(original_cwd)


if __name__ == '__main__':
    unittest.main()