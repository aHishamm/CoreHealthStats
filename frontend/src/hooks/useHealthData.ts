import { useState, useEffect, useCallback } from 'react';
import HealthAnalyticsAPI from '../services/api';
import {
  Workout,
  DailyMetrics,
  NightlyMetrics,
  HealthSummary,
  WorkoutFilter,
  DateRange,
  ApiResponse
} from '../types/health';

// Custom hook for fetching workouts
export const useWorkouts = (filter?: WorkoutFilter) => {
  const [workouts, setWorkouts] = useState<Workout[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkouts = useCallback(async () => {
    try {
      setLoading(true);
      const response = await HealthAnalyticsAPI.getWorkouts(filter);
      setWorkouts(response.results);
      setError(null);
    } catch (err) {
      setError('Failed to fetch workouts');
      console.error(err);
      // Provide empty data if API fails
      setWorkouts([]);
    } finally {
      setLoading(false);
    }
  }, [filter]);

  useEffect(() => {
    fetchWorkouts();
  }, [fetchWorkouts]);

  return { workouts, loading, error, refetch: fetchWorkouts };
};

// Custom hook for fetching daily metrics
export const useDailyMetrics = (dateRange?: DateRange) => {
  const [dailyMetrics, setDailyMetrics] = useState<DailyMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDailyMetrics = async () => {
      try {
        setLoading(true);
        const response = await HealthAnalyticsAPI.getDailyMetrics(dateRange);
        setDailyMetrics(response.results);
        setError(null);
      } catch (err) {
        setError('Failed to fetch daily metrics');
        console.error(err);
        // Provide empty data if API fails
        setDailyMetrics([]);
      } finally {
        setLoading(false);
      }
    };

    fetchDailyMetrics();
  }, [dateRange]);

  return { dailyMetrics, loading, error };
};

// Custom hook for fetching nightly metrics
export const useNightlyMetrics = (dateRange?: DateRange) => {
  const [nightlyMetrics, setNightlyMetrics] = useState<NightlyMetrics[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchNightlyMetrics = async () => {
      try {
        setLoading(true);
        const response = await HealthAnalyticsAPI.getNightlyMetrics(dateRange);
        setNightlyMetrics(response.results);
        setError(null);
      } catch (err) {
        setError('Failed to fetch nightly metrics');
        console.error(err);
        // Provide empty data if API fails
        setNightlyMetrics([]);
      } finally {
        setLoading(false);
      }
    };

    fetchNightlyMetrics();
  }, [dateRange]);

  return { nightlyMetrics, loading, error };
};

// Custom hook for health summary
export const useHealthSummary = (dateRange: DateRange) => {
  const [summary, setSummary] = useState<HealthSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        setLoading(true);
        const response = await HealthAnalyticsAPI.getHealthSummary(dateRange);
        setSummary(response);
        setError(null);
      } catch (err) {
        setError('Failed to fetch health summary');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (dateRange.start_date && dateRange.end_date) {
      fetchSummary();
    }
  }, [dateRange]);

  return { summary, loading, error };
};

// Custom hook for workout trends
export const useWorkoutTrends = (dateRange: DateRange) => {
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        setLoading(true);
        const response = await HealthAnalyticsAPI.getWorkoutTrends(dateRange);
        setTrends(response);
        setError(null);
      } catch (err) {
        setError('Failed to fetch workout trends');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (dateRange.start_date && dateRange.end_date) {
      fetchTrends();
    }
  }, [dateRange]);

  return { trends, loading, error };
};

// Custom hook for daily trends
export const useDailyTrends = (dateRange: DateRange) => {
  const [trends, setTrends] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrends = async () => {
      try {
        setLoading(true);
        const response = await HealthAnalyticsAPI.getDailyTrends(dateRange);
        setTrends(response);
        setError(null);
      } catch (err) {
        setError('Failed to fetch daily trends');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    if (dateRange.start_date && dateRange.end_date) {
      fetchTrends();
    }
  }, [dateRange]);

  return { trends, loading, error };
};

// Custom hook for authentication state
export const useAuth = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(
    HealthAnalyticsAPI.isAuthenticated()
  );

  const login = async (username: string, password: string) => {
    try {
      await HealthAnalyticsAPI.login(username, password);
      setIsAuthenticated(true);
      return true;
    } catch (error) {
      throw error;
    }
  };

  const logout = async () => {
    await HealthAnalyticsAPI.logout();
    setIsAuthenticated(false);
  };

  return { isAuthenticated, login, logout };
};
