import dayjs from 'dayjs';
import { Workout, DailyMetrics, HeartRateZoneData } from '../types/health';

// Date formatting utilities
export const formatDate = (date: string | Date): string => {
  return dayjs(date).format('YYYY-MM-DD');
};

export const formatDateTime = (date: string | Date): string => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss');
};

export const formatDisplayDate = (date: string | Date): string => {
  return dayjs(date).format('MMM DD, YYYY');
};

export const formatDisplayDateTime = (date: string | Date): string => {
  return dayjs(date).format('MMM DD, YYYY HH:mm');
};

// Time duration formatting
export const formatDuration = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  
  if (hours > 0) {
    return `${hours}h ${mins}m`;
  }
  return `${mins}m`;
};

export const formatDurationDetailed = (minutes: number): string => {
  const hours = Math.floor(minutes / 60);
  const mins = Math.round(minutes % 60);
  
  if (hours > 0) {
    return `${hours} hour${hours !== 1 ? 's' : ''} ${mins} minute${mins !== 1 ? 's' : ''}`;
  }
  return `${mins} minute${mins !== 1 ? 's' : ''}`;
};

// Distance formatting
export const formatDistance = (distance: number, unit: string = 'km'): string => {
  if (unit.toLowerCase() === 'km') {
    return `${distance.toFixed(2)} km`;
  }
  return `${distance.toFixed(2)} ${unit}`;
};

// Energy formatting
export const formatEnergy = (energy: number, unit: string = 'kcal'): string => {
  return `${Math.round(energy)} ${unit}`;
};

// Heart rate zone calculations
export const calculateHeartRateZones = (maxHR: number): HeartRateZoneData[] => {
  return [
    {
      zone: 'Zone 1 (Recovery)',
      percentage: 50,
      time: maxHR * 0.5,
      color: '#4FC3F7'
    },
    {
      zone: 'Zone 2 (Aerobic)',
      percentage: 60,
      time: maxHR * 0.6,
      color: '#81C784'
    },
    {
      zone: 'Zone 3 (Threshold)',
      percentage: 70,
      time: maxHR * 0.7,
      color: '#FFB74D'
    },
    {
      zone: 'Zone 4 (VO2 Max)',
      percentage: 80,
      time: maxHR * 0.8,
      color: '#FF8A65'
    },
    {
      zone: 'Zone 5 (Anaerobic)',
      percentage: 90,
      time: maxHR * 0.9,
      color: '#F06292'
    }
  ];
};

// Workout type formatting
export const formatWorkoutType = (workoutType: string): string => {
  return workoutType
    .split(/(?=[A-Z])/) // Split on capital letters
    .join(' ')
    .toLowerCase()
    .replace(/\b\w/g, l => l.toUpperCase()); // Capitalize first letter of each word
};

// Color utilities for charts
export const getWorkoutTypeColor = (workoutType: string): string => {
  const colors: { [key: string]: string } = {
    'running': '#FF6B6B',
    'cycling': '#4ECDC4',
    'swimming': '#45B7D1',
    'walking': '#96CEB4',
    'hiking': '#FFEAA7',
    'strength training': '#DDA0DD',
    'yoga': '#98D8C8',
    'other': '#A8A8A8'
  };
  
  const normalized = workoutType.toLowerCase();
  return colors[normalized] || colors['other'];
};

// Statistics utilities
export const calculateAverage = (values: number[]): number => {
  if (values.length === 0) return 0;
  return values.reduce((sum, value) => sum + value, 0) / values.length;
};

export const calculateMax = (values: number[]): number => {
  if (values.length === 0) return 0;
  return Math.max(...values);
};

export const calculateMin = (values: number[]): number => {
  if (values.length === 0) return 0;
  return Math.min(...values);
};

export const calculateSum = (values: number[]): number => {
  return values.reduce((sum, value) => sum + value, 0);
};

// Data transformation utilities
export const groupWorkoutsByDate = (workouts: Workout[]) => {
  return workouts.reduce((groups, workout) => {
    const date = formatDate(workout.start_date);
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(workout);
    return groups;
  }, {} as { [key: string]: Workout[] });
};

export const groupDailyMetricsByDate = (metrics: DailyMetrics[]) => {
  return metrics.reduce((groups, metric) => {
    const date = metric.date;
    groups[date] = metric;
    return groups;
  }, {} as { [key: string]: DailyMetrics });
};

// Date range utilities
export const getLastNDays = (days: number): { start_date: string; end_date: string } => {
  const endDate = dayjs();
  const startDate = endDate.subtract(days, 'day');
  
  return {
    start_date: startDate.format('YYYY-MM-DD'),
    end_date: endDate.format('YYYY-MM-DD')
  };
};

export const getThisWeek = (): { start_date: string; end_date: string } => {
  const startOfWeek = dayjs().startOf('week');
  const endOfWeek = dayjs().endOf('week');
  
  return {
    start_date: startOfWeek.format('YYYY-MM-DD'),
    end_date: endOfWeek.format('YYYY-MM-DD')
  };
};

export const getThisMonth = (): { start_date: string; end_date: string } => {
  const startOfMonth = dayjs().startOf('month');
  const endOfMonth = dayjs().endOf('month');
  
  return {
    start_date: startOfMonth.format('YYYY-MM-DD'),
    end_date: endOfMonth.format('YYYY-MM-DD')
  };
};

// Validation utilities
export const isValidEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const isValidPassword = (password: string): boolean => {
  return password.length >= 8;
};

// Number formatting utilities
export const formatNumber = (num: number, decimals: number = 0): string => {
  return num.toLocaleString(undefined, {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals
  });
};

export const formatPercentage = (num: number, decimals: number = 1): string => {
  return `${(num * 100).toFixed(decimals)}%`;
};
