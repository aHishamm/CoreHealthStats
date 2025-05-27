import React, { useState } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Typography,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent
} from '@mui/material';
import {
  Info,
  FitnessCenter,
  Timer,
  Straighten,
  LocalFireDepartment
} from '@mui/icons-material';
import { useWorkouts } from '../../hooks/useHealthData';
import {
  formatDuration,
  formatDistance,
  formatEnergy,
  formatDisplayDateTime,
  formatWorkoutType,
  getWorkoutTypeColor,
  getLastNDays
} from '../../utils/helpers';
import { Workout } from '../../types/health';
import WorkoutBarChart from '../charts/WorkoutBarChart';
import HeartRateZoneChart from '../charts/HeartRateZoneChart';

const WorkoutView: React.FC = () => {
  const [selectedWorkout, setSelectedWorkout] = useState<Workout | null>(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [activityFilter, setActivityFilter] = useState('all');
  const [timeRange, setTimeRange] = useState('30days');

  const getDateRange = () => {
    switch (timeRange) {
      case '7days':
        return getLastNDays(7);
      case '30days':
        return getLastNDays(30);
      case '90days':
        return getLastNDays(90);
      default:
        return getLastNDays(30);
    }
  };

  const dateRange = getDateRange();
  const { workouts, loading } = useWorkouts({
    ...dateRange,
    workout_activity_type: activityFilter !== 'all' ? activityFilter : undefined
  });

  const handleWorkoutClick = (workout: Workout) => {
    setSelectedWorkout(workout);
    setDialogOpen(true);
  };

  const handleCloseDialog = () => {
    setDialogOpen(false);
    setSelectedWorkout(null);
  };

  const handleActivityFilterChange = (event: SelectChangeEvent) => {
    setActivityFilter(event.target.value);
  };

  const handleTimeRangeChange = (event: SelectChangeEvent) => {
    setTimeRange(event.target.value);
  };

  // Get unique activity types for filter
  const activityTypes = Array.from(new Set(workouts.map(w => w.workout_activity_type)));

  // Prepare chart data
  const workoutChartData = workouts.map(workout => ({
    date: workout.start_date,
    duration: workout.duration,
    distance: workout.total_distance || 0,
    energy: workout.total_energy_burned || 0,
    heart_rate: workout.avg_heart_rate || 0,
    trimp_score: workout.trimp_score || 0,
    activity_type: workout.workout_activity_type,
  }));

  if (loading) {
    return (
      <Box p={3}>
        <Typography>Loading workouts...</Typography>
      </Box>
    );
  }

  return (
    <Box p={3}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Workouts
        </Typography>
        <Box display="flex" gap={2}>
          <FormControl variant="outlined" size="small" sx={{ minWidth: 140 }}>
            <InputLabel>Activity Type</InputLabel>
            <Select
              value={activityFilter}
              onChange={handleActivityFilterChange}
              label="Activity Type"
            >
              <MenuItem value="all">All Activities</MenuItem>
              {activityTypes.map(type => (
                <MenuItem key={type} value={type}>
                  {formatWorkoutType(type)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Time Range</InputLabel>
            <Select
              value={timeRange}
              onChange={handleTimeRangeChange}
              label="Time Range"
            >
              <MenuItem value="7days">Last 7 Days</MenuItem>
              <MenuItem value="30days">Last 30 Days</MenuItem>
              <MenuItem value="90days">Last 90 Days</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>

      {/* Charts */}
      <Grid container spacing={3} mb={4}>
        <Grid size={{ xs: 12, md: 6 }}>
          <WorkoutBarChart
            data={workoutChartData}
            title="Workout Duration"
            dataKey="duration"
            unit="min"
          />
        </Grid>
        <Grid size={{ xs: 12, md: 6 }}>
          <WorkoutBarChart
            data={workoutChartData.filter(w => w.energy > 0)}
            title="Energy Burned"
            dataKey="energy"
            unit="kcal"
          />
        </Grid>
      </Grid>

      {/* Workouts Table */}
      <Paper elevation={2}>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Activity</TableCell>
                <TableCell>Date</TableCell>
                <TableCell align="right">Duration</TableCell>
                <TableCell align="right">Distance</TableCell>
                <TableCell align="right">Energy</TableCell>
                <TableCell align="right">Avg HR</TableCell>
                <TableCell align="center">Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {workouts.map((workout) => (
                <TableRow key={workout.id} hover>
                  <TableCell>
                    <Chip
                      label={formatWorkoutType(workout.workout_activity_type)}
                      sx={{
                        backgroundColor: getWorkoutTypeColor(workout.workout_activity_type),
                        color: 'white'
                      }}
                      size="small"
                    />
                  </TableCell>
                  <TableCell>
                    {formatDisplayDateTime(workout.start_date)}
                  </TableCell>
                  <TableCell align="right">
                    {formatDuration(workout.duration)}
                  </TableCell>
                  <TableCell align="right">
                    {workout.total_distance ? formatDistance(workout.total_distance) : '-'}
                  </TableCell>
                  <TableCell align="right">
                    {workout.total_energy_burned ? formatEnergy(workout.total_energy_burned) : '-'}
                  </TableCell>
                  <TableCell align="right">
                    {workout.avg_heart_rate ? `${workout.avg_heart_rate.toFixed(0)} bpm` : '-'}
                  </TableCell>
                  <TableCell align="center">
                    <IconButton
                      size="small"
                      onClick={() => handleWorkoutClick(workout)}
                      color="primary"
                    >
                      <Info />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Workout Detail Dialog */}
      <Dialog open={dialogOpen} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        {selectedWorkout && (
          <>
            <DialogTitle>
              <Box display="flex" alignItems="center" gap={2}>
                <FitnessCenter color="primary" />
                <Typography variant="h6">
                  {formatWorkoutType(selectedWorkout.workout_activity_type)} Details
                </Typography>
              </Box>
            </DialogTitle>
            <DialogContent>
              <Grid container spacing={3}>
                <Grid size={{ xs: 12, md: 6 }}>
                  <Card>
                    <CardContent>
                      <Box display="flex" alignItems="center" gap={1} mb={2}>
                        <Timer color="primary" />
                        <Typography variant="h6">Duration</Typography>
                      </Box>
                      <Typography variant="h4">
                        {formatDuration(selectedWorkout.duration)}
                      </Typography>
                    </CardContent>
                  </Card>
                </Grid>
                
                {selectedWorkout.total_distance && (
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                      <CardContent>
                        <Box display="flex" alignItems="center" gap={1} mb={2}>
                          <Straighten color="primary" />
                          <Typography variant="h6">Distance</Typography>
                        </Box>
                        <Typography variant="h4">
                          {formatDistance(selectedWorkout.total_distance)}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}
                
                {selectedWorkout.total_energy_burned && (
                  <Grid size={{ xs: 12, md: 6 }}>
                    <Card>
                      <CardContent>
                        <Box display="flex" alignItems="center" gap={1} mb={2}>
                          <LocalFireDepartment color="primary" />
                          <Typography variant="h6">Energy Burned</Typography>
                        </Box>
                        <Typography variant="h4">
                          {formatEnergy(selectedWorkout.total_energy_burned)}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                )}

                <Grid size={12}>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Start Time:</strong> {formatDisplayDateTime(selectedWorkout.start_date)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>End Time:</strong> {formatDisplayDateTime(selectedWorkout.end_date)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    <strong>Source:</strong> {selectedWorkout.source_name}
                  </Typography>
                  {selectedWorkout.device && (
                    <Typography variant="body2" color="text.secondary">
                      <strong>Device:</strong> {selectedWorkout.device}
                    </Typography>
                  )}
                </Grid>
              </Grid>
            </DialogContent>
            <DialogActions>
              <Button onClick={handleCloseDialog}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>
    </Box>
  );
};

export default WorkoutView;
