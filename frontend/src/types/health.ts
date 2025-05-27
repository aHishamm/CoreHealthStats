// Health Analytics Types
export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
}

export interface HealthDataUpload {
  id: number;
  user: number | null;
  file: string;
  upload_date: string;
  processed: boolean;
  processing_status: string;
  error_message: string | null;
  total_records: number;
}

export interface HealthRecord {
  id: number;
  upload: number;
  type: string;
  source_name: string;
  source_version: string | null;
  device: string | null;
  unit: string;
  creation_date: string;
  start_date: string;
  end_date: string;
  value: string;
}

export interface Workout {
  id: number;
  upload: number;
  workout_activity_type: string;
  duration: number;
  duration_unit: string;
  total_distance: number | null;
  total_distance_unit: string | null;
  total_energy_burned: number | null;
  total_energy_burned_unit: string | null;
  source_name: string;
  source_version: string | null;
  device: string | null;
  creation_date: string;
  start_date: string;
  end_date: string;
  avg_heart_rate?: number;
  max_heart_rate?: number;
  trimp_score?: number;
}

export interface DailyMetrics {
  id: number;
  user: number | null;
  date: string;
  avg_heart_rate: number | null;
  max_heart_rate: number | null;
  min_heart_rate: number | null;
  resting_heart_rate: number | null;
  step_count: number | null;
  distance_walking_running: number | null;
  active_energy_burned: number | null;
  basal_energy_burned: number | null;
  flights_climbed: number | null;
  vo2_max: number | null;
}

export interface NightlyMetrics {
  id: number;
  user: number | null;
  date: string;
  sleep_duration: number | null;
  time_in_bed: number | null;
  sleep_efficiency: number | null;
  avg_heart_rate_sleep: number | null;
}

export interface UserProfile {
  id: number;
  user: number;
  date_of_birth: string | null;
  gender: string | null;
  height: number | null;
  weight: number | null;
  activity_level: string;
  created_at: string;
  updated_at: string;
}

export interface WorkoutAnalysis {
  workout: Workout;
  heart_rate_zones: {
    zone_1: number;
    zone_2: number;
    zone_3: number;
    zone_4: number;
    zone_5: number;
  };
  trimp_score: number;
  intensity_distribution: {
    easy: number;
    moderate: number;
    hard: number;
  };
}

export interface HealthSummary {
  date_range: {
    start_date: string;
    end_date: string;
  };
  workout_summary: {
    total_workouts: number;
    total_duration: number;
    total_distance: number;
    total_energy_burned: number;
    avg_trimp_score: number;
  };
  heart_rate_summary: {
    avg_resting_hr: number;
    avg_max_hr: number;
    hr_variability: number;
  };
  activity_summary: {
    avg_daily_steps: number;
    avg_daily_distance: number;
    avg_daily_energy: number;
  };
  sleep_summary: {
    avg_sleep_duration: number;
    avg_sleep_efficiency: number;
    total_nights: number;
  };
}

export interface ApiResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface DateRange {
  start_date: string;
  end_date: string;
}

export interface WorkoutFilter {
  workout_activity_type?: string;
  start_date?: string;
  end_date?: string;
  min_duration?: number;
  max_duration?: number;
}

// Chart data types
export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface WorkoutChartData {
  date: string;
  duration: number;
  distance?: number;
  energy?: number;
  heart_rate?: number;
  trimp_score?: number;
  activity_type: string;
}

export interface HeartRateZoneData {
  zone: string;
  percentage: number;
  time: number;
  color: string;
}
