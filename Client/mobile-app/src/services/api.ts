import axios, {AxiosInstance} from 'axios';
import {API_CONFIG, buildBackendUrl} from '../config/api';
import AsyncStorage from '@react-native-async-storage/async-storage';

export interface Floor {
  id: number;
  building_id: number;
  floor_number: number;
  name: string | null;
}

export interface Camera {
  id: number;
  floor_id: number;
  name: string;
  rtsp_url: string;
  position_x: number | null;
  position_y: number | null;
  position_z: number | null;
  is_active: boolean;
}

export interface Alert {
  id: number;
  event_type: string;
  floor_id: number;
  fire_event_id: number | null;
  severity: string;
  status: string;
  created_at: string;
  resolved_at: string | null;
  screenshot_path?: string;
  confidence?: number;
}

export interface Employee {
  id: number;
  name: string;
  employee_number: string;
  department: string;
  face_photo_path?: string;
}

class ApiClient {
  private client: AxiosInstance;
  private maxRetries: number = 3;
  private retryDelay: number = 1000;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BACKEND_API,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    });

    // Add request interceptor for auth token
    this.client.interceptors.request.use(
      async config => {
        const token = await AsyncStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`, {
          baseURL: config.baseURL,
          hasToken: !!token,
        });
        return config;
      },
      error => Promise.reject(error),
    );

    // Add response interceptor for logging
    this.client.interceptors.response.use(
      response => {
        const url = response.config.url || '';
        console.log(`[API] Response ${url}:`, {
          status: response.status,
          dataLength: Array.isArray(response.data) ? response.data.length : 'not array',
        });
        // Log full response for cameras endpoint to debug
        if (url.includes('/cameras') && !url.includes('/cameras/')) {
          console.log(`[API] Cameras response data:`, JSON.stringify(response.data, null, 2));
        }
        return response;
      },
      error => {
        console.error(`[API] Error ${error.config?.url}:`, {
          status: error.response?.status,
          message: error.message,
          data: error.response?.data,
          fullError: JSON.stringify(error.response?.data || error.message, null, 2),
        });
        return Promise.reject(error);
      },
    );
  }

  private async retryRequest<T>(
    requestFn: () => Promise<T>,
    retries = this.maxRetries,
  ): Promise<T> {
    try {
      return await requestFn();
    } catch (error: any) {
      if (retries > 0 && error.response?.status >= 500) {
        await new Promise(resolve => setTimeout(resolve, this.retryDelay));
        return this.retryRequest(requestFn, retries - 1);
      }
      throw error;
    }
  }

  // Authentication
  async login(email: string, password: string): Promise<{token: string; user: any}> {
    const response = await this.client.post('/auth/login/json', {email, password});
    if (response.data.token) {
      await AsyncStorage.setItem('auth_token', response.data.token);
    }
    return response.data;
  }

  async logout(): Promise<void> {
    await AsyncStorage.removeItem('auth_token');
  }

  // Floors
  async getFloors(): Promise<Floor[]> {
    return this.retryRequest(async () => {
      const response = await this.client.get('/floors');
      // Backend may return array directly or wrapped in object
      if (Array.isArray(response.data)) {
        return response.data;
      } else if (response.data && Array.isArray(response.data.data)) {
        return response.data.data;
      } else if (response.data && Array.isArray(response.data.floors)) {
        return response.data.floors;
      }
      return [];
    });
  }

  async getFloor(id: number): Promise<Floor> {
    return this.retryRequest(async () => {
      const response = await this.client.get(`/floors/${id}`);
      return response.data;
    });
  }

  // Cameras
  async getCameras(): Promise<Camera[]> {
    return this.retryRequest(async () => {
      const response = await this.client.get('/cameras');
      console.log('[API] getCameras raw response:', JSON.stringify(response.data, null, 2));
      console.log('[API] getCameras response type:', typeof response.data);
      console.log('[API] getCameras is array?', Array.isArray(response.data));
      
      // Backend may return array directly or wrapped in object
      if (Array.isArray(response.data)) {
        console.log('[API] getCameras returning array directly, length:', response.data.length);
        return response.data;
      } else if (response.data && Array.isArray(response.data.data)) {
        console.log('[API] getCameras returning response.data.data, length:', response.data.data.length);
        return response.data.data;
      } else if (response.data && Array.isArray(response.data.cameras)) {
        console.log('[API] getCameras returning response.data.cameras, length:', response.data.cameras.length);
        return response.data.cameras;
      }
      console.warn('[API] getCameras: No array found in response, returning empty array');
      console.warn('[API] getCameras response.data keys:', response.data ? Object.keys(response.data) : 'null');
      return [];
    });
  }

  async getCamera(id: number): Promise<Camera> {
    return this.retryRequest(async () => {
      const response = await this.client.get(`/cameras/${id}`);
      return response.data;
    });
  }

  // Alerts
  async getAlerts(params?: {limit?: number; status?: string}): Promise<Alert[]> {
    return this.retryRequest(async () => {
      const response = await this.client.get('/alerts', {params});
      // Backend returns {success: true, alerts: [...]}, extract the alerts array
      if (response.data && typeof response.data === 'object') {
        if (Array.isArray(response.data)) {
          return response.data;
        } else if (response.data.alerts && Array.isArray(response.data.alerts)) {
          return response.data.alerts;
        } else if (response.data.data && Array.isArray(response.data.data)) {
          return response.data.data;
        }
      }
      return [];
    });
  }

  async getAlert(id: number): Promise<Alert> {
    return this.retryRequest(async () => {
      const response = await this.client.get(`/alerts/${id}`);
      return response.data;
    });
  }

  // Employees
  async getEmployees(): Promise<Employee[]> {
    return this.retryRequest(async () => {
      const response = await this.client.get('/employees');
      return response.data;
    });
  }

  // Presence/Occupancy
  async getFloorOccupancy(floorId: number): Promise<{
    floor_id: number;
    person_count: number;
    people_list: Array<{
      track_id: string;
      employee_id: number | null;
      name: string | null;
      confidence: number;
    }>;
    timestamp: string;
  }> {
    return this.retryRequest(async () => {
      const response = await this.client.get(`/presence/floor-live/${floorId}`);
      return response.data;
    });
  }

  // Health check
  async healthCheck(): Promise<boolean> {
    try {
      const response = await this.client.get('/health');
      return response.status === 200;
    } catch {
      return false;
    }
  }
}

export default new ApiClient();
