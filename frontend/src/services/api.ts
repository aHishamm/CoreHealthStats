import axios, { AxiosResponse } from 'axios';
import {
  HealthDataUpload,
  HealthRecord,
  Workout,
  DailyMetrics,
  NightlyMetrics,
  UserProfile,
  WorkoutAnalysis,
  HealthSummary,
  ApiResponse,
  DateRange,
  WorkoutFilter
} from '../types/health';

// Base API configuration
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8000';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('authToken');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('authToken');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export class HealthAnalyticsAPI {
  // Auth endpoints
  static async login(username: string, password: string) {
    try {
      const response = await api.post('/auth/login/', { username, password });
      if (response.data.token) {
        localStorage.setItem('authToken', response.data.token);
      }
      return response.data;
    } catch (error) {
      throw error;
    }
  }

  static async logout() {
    try {
      await api.post('/auth/logout/');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('authToken');
    }
  }

  static async register(userData: {
    username: string;
    email: string;
    password: string;
    first_name?: string;
    last_name?: string;
  }) {
    const response = await api.post('/auth/register/', userData);
    return response.data;
  }

  // Health Data Upload endpoints
  static async uploadHealthData(file: File): Promise<HealthDataUpload> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/api/uploads/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }

  static async getUploads(): Promise<ApiResponse<HealthDataUpload>> {
    const response = await api.get('/api/uploads/');
    return response.data;
  }

  static async getUpload(id: number): Promise<HealthDataUpload> {
    const response = await api.get(`/api/uploads/${id}/`);
    return response.data;
  }

  // Health Records endpoints
  static async getHealthRecords(params?: {
    type?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<ApiResponse<HealthRecord>> {
    const response = await api.get('/api/records/', { params });
    return response.data;
  }

  static async getHealthRecord(id: number): Promise<HealthRecord> {
    const response = await api.get(`/api/records/${id}/`);
    return response.data;
  }

  // Workout endpoints
  static async getWorkouts(params?: WorkoutFilter & {
    page?: number;
    page_size?: number;
  }): Promise<ApiResponse<Workout>> {
    const response = await api.get('/api/workouts/', { params });
    return response.data;
  }

  static async getWorkout(id: number): Promise<Workout> {
    const response = await api.get(`/api/workouts/${id}/`);
    return response.data;
  }

  static async analyzeWorkout(id: number): Promise<WorkoutAnalysis> {
    const response = await api.get(`/api/workouts/${id}/analyze/`);
    return response.data;
  }

  static async getWorkoutTrends(params: DateRange): Promise<any> {
    const response = await api.get('/api/workouts/trends/', { params });
    return response.data;
  }

  // Daily Metrics endpoints
  static async getDailyMetrics(params?: {
    date?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<ApiResponse<DailyMetrics>> {
    const response = await api.get('/api/daily-metrics/', { params });
    return response.data;
  }

  static async getDailyMetric(id: number): Promise<DailyMetrics> {
    const response = await api.get(`/api/daily-metrics/${id}/`);
    return response.data;
  }

  static async getDailyTrends(params: DateRange): Promise<any> {
    const response = await api.get('/api/daily-metrics/trends/', { params });
    return response.data;
  }

  // Nightly Metrics endpoints
  static async getNightlyMetrics(params?: {
    date?: string;
    start_date?: string;
    end_date?: string;
    page?: number;
    page_size?: number;
  }): Promise<ApiResponse<NightlyMetrics>> {
    const response = await api.get('/api/nightly-metrics/', { params });
    return response.data;
  }

  static async getNightlyMetric(id: number): Promise<NightlyMetrics> {
    const response = await api.get(`/api/nightly-metrics/${id}/`);
    return response.data;
  }

  static async getSleepTrends(params: DateRange): Promise<any> {
    const response = await api.get('/api/nightly-metrics/trends/', { params });
    return response.data;
  }

  // User Profile endpoints
  static async getUserProfile(): Promise<UserProfile> {
    const response = await api.get('/api/profiles/me/');
    return response.data;
  }

  static async updateUserProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    const response = await api.patch('/api/profiles/me/', data);
    return response.data;
  }

  // Analytics endpoints
  static async getHealthSummary(params: DateRange): Promise<HealthSummary> {
    const response = await api.get('/api/analytics/summary/', { params });
    return response.data;
  }

  static async getHeartRateAnalysis(params: DateRange): Promise<any> {
    const response = await api.get('/api/analytics/heart-rate/', { params });
    return response.data;
  }

  static async getTrimpAnalysis(params: DateRange): Promise<any> {
    const response = await api.get('/api/analytics/trimp/', { params });
    return response.data;
  }

  // Utility methods
  static isAuthenticated(): boolean {
    return !!localStorage.getItem('authToken');
  }

  static getAuthToken(): string | null {
    return localStorage.getItem('authToken');
  }
}

export default HealthAnalyticsAPI;
