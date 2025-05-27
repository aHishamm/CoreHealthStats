import React, { useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import {
  FitnessCenter,
  Favorite,
  DirectionsWalk,
  LocalFireDepartment,
  Bedtime
} from '@mui/icons-material';
import StatsCard from './StatsCard';
import LineChartComponent from '../charts/LineChart';
import WorkoutBarChart from '../charts/WorkoutBarChart';
import {
  useWorkouts,
  useDailyMetrics,
  useNightlyMetrics,
  useHealthSummary
} from '../../hooks/useHealthData';
import {
  getLastNDays,
  getThisWeek,
  getThisMonth,
  formatDuration,
  formatDistance,
  formatEnergy,
  calculateAverage
} from '../../utils/helpers';
import { ChartDataPoint, WorkoutChartData } from '../../types/health';

const DashboardView: React.FC = () => {
  const [timeRange, setTimeRange] = useState('30days');
  
  const getDateRange = () => {
    switch (timeRange) {
      case '7days':
        return getLastNDays(7);
      case '30days':
        return getLastNDays(30);
      case 'week':
        return getThisWeek();
      case 'month':
        return getThisMonth();
      default:
        return getLastNDays(30);
    }
  };

  const dateRange = getDateRange();
  const { workouts, loading: workoutsLoading } = useWorkouts(dateRange);
  const { dailyMetrics, loading: dailyLoading } = useDailyMetrics(dateRange);
  const { nightlyMetrics, loading: sleepLoading } = useNightlyMetrics(dateRange);
  const { summary, loading: summaryLoading } = useHealthSummary(dateRange);

  const handleTimeRangeChange = (event: SelectChangeEvent) => {
    setTimeRange(event.target.value);
  };

  // Prepare chart data
  const heartRateData: ChartDataPoint[] = dailyMetrics
    .filter(metric => metric.avg_heart_rate)
    .map(metric => ({
      date: metric.date,
      value: metric.avg_heart_rate!,
    }));

  const stepCountData: ChartDataPoint[] = dailyMetrics
    .filter(metric => metric.step_count)
    .map(metric => ({
      date: metric.date,
      value: metric.step_count!,
    }));

  const workoutChartData: WorkoutChartData[] = workouts.map(workout => ({
    date: workout.start_date,
    duration: workout.duration,
    distance: workout.total_distance || 0,
    energy: workout.total_energy_burned || 0,
    heart_rate: workout.avg_heart_rate || 0,
    trimp_score: workout.trimp_score || 0,
    activity_type: workout.workout_activity_type,
  }));

  const sleepData: ChartDataPoint[] = nightlyMetrics
    .filter(metric => metric.sleep_duration)
    .map(metric => ({
      date: metric.date,
      value: metric.sleep_duration! / 60, // Convert to hours
    }));

  // Calculate summary stats
  const avgHeartRate = calculateAverage(
    dailyMetrics.filter(m => m.avg_heart_rate).map(m => m.avg_heart_rate!)
  );
  const totalSteps = dailyMetrics.reduce((sum, m) => sum + (m.step_count || 0), 0);
  const totalWorkouts = workouts.length;
  const totalWorkoutTime = workouts.reduce((sum, w) => sum + w.duration, 0);
  const avgSleepDuration = calculateAverage(
    nightlyMetrics.filter(m => m.sleep_duration).map(m => m.sleep_duration!)
  ) / 60; // Convert to hours

  if (workoutsLoading || dailyLoading || sleepLoading || summaryLoading) {
    return (
      <Box p={3}>
        <Typography>Loading dashboard...</Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Health Dashboard
        </Typography>
        <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange}
            onChange={handleTimeRangeChange}
            label="Time Range"
          >
            <MenuItem value="7days">Last 7 Days</MenuItem>
            <MenuItem value="30days">Last 30 Days</MenuItem>
            <MenuItem value="week">This Week</MenuItem>
            <MenuItem value="month">This Month</MenuItem>
          </Select>
        </FormControl>
      </Box>

      {/* Stats Cards */}
      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatsCard
            title="Total Workouts"
            value={totalWorkouts}
            icon={<FitnessCenter />}
            color="primary"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatsCard
            title="Avg Heart Rate"
            value={avgHeartRate.toFixed(0)}
            unit="bpm"
            icon={<Favorite />}
            color="error"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatsCard
            title="Total Steps"
            value={totalSteps}
            icon={<DirectionsWalk />}
            color="success"
          />
        </Grid>
        <Grid size={{ xs: 12, sm: 6, md: 3 }}>
          <StatsCard
            title="Avg Sleep"
            value={avgSleepDuration.toFixed(1)}
            unit="hours"
            icon={<Bedtime />}
            color="secondary"
          />
        </Grid>
      </Grid>

      {/* Charts */}
      <Grid container spacing={3}>
        <Grid size={{ xs: 12, md: 6 }}>
          <LineChartComponent
            data={heartRateData}
            title="Average Heart Rate Trend"
            dataKey="value"
            unit="bpm"
            color="#f44336"
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <LineChartComponent
            data={stepCountData}
            title="Daily Step Count"
            dataKey="value"
            unit="steps"
            color="#4caf50"
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <WorkoutBarChart
            data={workoutChartData}
            title="Workout Duration"
            dataKey="duration"
            unit="min"
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <LineChartComponent
            data={sleepData}
            title="Sleep Duration"
            dataKey="value"
            unit="hours"
            color="#9c27b0"
          />
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardView;
