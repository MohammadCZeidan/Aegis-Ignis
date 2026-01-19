const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

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

export interface Occupancy {
  floor_id: number;
  person_count: number;
  people_list: Array<{
    track_id: string;
    employee_id: number | null;
    name: string | null;
    confidence: number;
  }>;
  timestamp: string;
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
}

class ApiClient {
  private baseUrl: string;
  private maxRetries: number = 3;
  private retryDelay: number = 1000; // ms

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('aegis_auth_token');
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
  }

  private async sleep(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  private async request<T>(endpoint: string, options?: RequestInit, retryCount: number = 0): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...this.getAuthHeaders(),
          ...options?.headers,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Unauthorized - clear auth and redirect to login
          localStorage.removeItem('aegis_auth_token');
          localStorage.removeItem('aegis_user');
          window.location.href = '/';
          throw new Error('Unauthorized');
        }

        if (response.status === 429) {
          // Rate limited - wait and retry
          const retryAfter = response.headers.get('Retry-After');
          const delay = retryAfter ? parseInt(retryAfter) * 1000 : this.retryDelay;
          
          if (retryCount < this.maxRetries) {
            console.warn(`Rate limited. Retrying after ${delay}ms...`);
            await this.sleep(delay);
            return this.request<T>(endpoint, options, retryCount + 1);
          }
        }

        // Try to parse error response
        const errorData = await response.json().catch(() => ({ message: response.statusText }));
        throw new Error(errorData.message || errorData.detail || `API error: ${response.statusText}`);
      }

      return response.json();
      
    } catch (error) {
      // Retry on network errors
      if (retryCount < this.maxRetries && error instanceof TypeError) {
        console.warn(`Network error. Retrying (${retryCount + 1}/${this.maxRetries})...`);
        await this.sleep(this.retryDelay * (retryCount + 1)); // Exponential backoff
        return this.request<T>(endpoint, options, retryCount + 1);
      }
      throw error;
    }
  }

  async healthCheck(): Promise<{ status: string; checks: any }> {
    return this.request('/health');
  }

  // Floors
  async getFloors(): Promise<Floor[]> {
    return this.request<Floor[]>('/floors');
  }

  async getFloor(floorId: number): Promise<Floor> {
    return this.request<Floor>(`/floors/${floorId}`);
  }

  // Cameras
  async getCameras(floorId?: number): Promise<Camera[]> {
    const params = floorId ? `?floor_id=${floorId}` : '';
    return this.request<Camera[]>(`/cameras${params}`);
  }

  async getCamera(cameraId: number): Promise<Camera> {
    return this.request<Camera>(`/cameras/${cameraId}`);
  }

  async getCameraStream(cameraId: number): Promise<{ camera_id: number; rtsp_url: string; stream_url: string }> {
    return this.request(`/cameras/${cameraId}/stream`);
  }

  // Occupancy
  async getFloorOccupancy(floorId: number): Promise<Occupancy> {
    return this.request<Occupancy>(`/floors/${floorId}/occupancy`);
  }

  async getOccupancySummary(): Promise<{ total_occupancy: number; floors: Array<{ floor_id: number; person_count: number }> }> {
    return this.request('/occupancy/summary');
  }

  // Alerts
  async getAlerts(params?: { status?: string; event_type?: string; floor_id?: number }): Promise<Alert[]> {
    const queryParams = new URLSearchParams();
    if (params?.status) queryParams.append('status', params.status);
    if (params?.event_type) queryParams.append('event_type', params.event_type);
    if (params?.floor_id) queryParams.append('floor_id', params.floor_id.toString());
    
    const query = queryParams.toString();
    return this.request<Alert[]>(`/alerts${query ? `?${query}` : ''}`);
  }

  async getAlert(alertId: number): Promise<Alert> {
    return this.request<Alert>(`/alerts/${alertId}`);
  }

  async acknowledgeAlert(alertId: number, acknowledgedBy: string): Promise<void> {
    return this.request(`/alerts/${alertId}/acknowledge`, {
      method: 'POST',
      body: JSON.stringify({ acknowledged_by: acknowledgedBy }),
    });
  }

  // Employees
  async getEmployees(floorId?: number): Promise<{ employees: any[]; total: number }> {
    const params = floorId ? `?floor_id=${floorId}` : '';
    return this.request(`/employees${params}`);
  }

  async getEmployeesByFloor(floorId: number): Promise<{ employees: any[]; total: number }> {
    return this.request(`/employees/by-floor/${floorId}`);
  }
}

export const api = new ApiClient();

