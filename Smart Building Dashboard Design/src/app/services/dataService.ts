/**
 * Data Management Service
 * Handles all CRUD operations for floors, cameras, employees
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://35.180.117.85/api/v1';

export interface Floor {
  id: number;
  name: string;
  floor_number: number;
  building_id?: number;
  description?: string;
  max_occupancy?: number;
  created_at?: string;
}

export interface Camera {
  id: number;
  name: string;
  floor_id: number;
  room?: string;
  rtsp_url?: string;
  is_active: boolean;
  stream_url?: string;
}

export interface Employee {
  id: number;
  name: string;
  email: string | null;
  employee_number?: string;
  department?: string | null;
  role?: string | null;
  status?: string;
  floor_id: number | null;
  floor_name?: string | null;
  current_floor_id?: number | null;
  current_room?: string | null;
  face_photo_path?: string | null;
  face_registered_at?: string | null;
  face_match_confidence?: string | null;
  photo_url: string | null;
  last_seen_at?: string | null;
  created_at?: string;
  updated_at?: string;
}

class DataService {
  private cache: Map<string, { data: any; timestamp: number }> = new Map();
  private readonly CACHE_DURATION = 30000; // 30 seconds cache

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('aegis_auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  private getCachedData<T>(key: string): T | null {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.CACHE_DURATION) {
      return cached.data as T;
    }
    return null;
  }

  private setCachedData(key: string, data: any): void {
    this.cache.set(key, { data, timestamp: Date.now() });
  }

  clearCache(): void {
    this.cache.clear();
  }

  // ============ FLOORS ============
  async getFloors(): Promise<Floor[]> {
    const cacheKey = 'floors';
    const cached = this.getCachedData<Floor[]>(cacheKey);
    if (cached) return cached;

    try {
      console.log('Fetching floors from:', `${API_BASE_URL}/floors`);
      const headers = this.getAuthHeaders();
      console.log('Auth headers:', headers);
      
      const response = await fetch(`${API_BASE_URL}/floors`, {
        headers,
      });
      
      console.log('Floors response status:', response.status);
      
      if (response.ok) {
        const data = await response.json();
        console.log('Floors response data:', data);
        
        // Handle different response formats
        let floors = data.floors || data.data || data;
        
        // Ensure we have an array
        if (!Array.isArray(floors)) {
          console.error('Floors response is not an array:', typeof floors, floors);
          floors = [];
        }
        
        console.log('Parsed floors:', floors);
        this.setCachedData(cacheKey, floors);
        return floors;
      } else {
        const errorText = await response.text();
        console.error('Failed to fetch floors. Status:', response.status, 'Error:', errorText);
      }
    } catch (error) {
      console.error('Failed to fetch floors:', error);
    }
    return [];
  }

  async createFloor(floor: Partial<Floor>): Promise<Floor | null> {
    try {
      // Ensure building_id is set (default to 1 if not provided)
      const floorData = {
        ...floor,
        building_id: floor.building_id || 1,
      };
      
      console.log('Sending floor creation request:', floorData);
      
      const response = await fetch(`${API_BASE_URL}/floors`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(floorData),
      });
      
      console.log('Response status:', response.status);
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Floor creation failed:', response.status, errorText);
        alert(`Failed to create floor: ${response.status} - ${errorText.substring(0, 100)}`);
        throw new Error(`Failed to create floor: ${response.status}`);
      }
      
      const data = await response.json();
      console.log('Floor created successfully:', data);
      this.cache.delete('floors'); // Clear cache
      return data.floor || data.data || data;
    } catch (error) {
      console.error('Failed to create floor:', error);
      if (error instanceof Error && !error.message.includes('Failed to create floor')) {
        alert('Failed to create floor. Make sure you are logged in and the backend is running.');
      }
      return null;
    }
  }

  async updateFloor(id: number, floor: Partial<Floor>): Promise<Floor | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/floors/${id}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(floor),
      });
      if (response.ok) {
        const data = await response.json();
        this.cache.delete('floors'); // Clear cache
        return data.floor || data.data;
      }
    } catch (error) {
      console.error('Failed to update floor:', error);
    }
    return null;
  }

  async deleteFloor(id: number): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/floors/${id}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });
      if (response.ok) {
        this.cache.delete('floors'); // Clear cache
      }
      return response.ok;
    } catch (error) {
      console.error('Failed to delete floor:', error);
      return false;
    }
  }

  // ============ CAMERAS ============
  async getCameras(): Promise<Camera[]> {
    const cacheKey = 'cameras';
    const cached = this.getCachedData<Camera[]>(cacheKey);
    if (cached) return cached;

    try {
      // Try streaming server first with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 2000); // 2 second timeout
      
      const streamResponse = await fetch('http://localhost:5000/api/cameras', {
        signal: controller.signal
      });
      clearTimeout(timeoutId);
      
      if (streamResponse.ok) {
        const data = await streamResponse.json();
        if (data.success && data.cameras) {
          const cameras = data.cameras.map((cam: any) => ({
            id: cam.id,
            name: cam.name,
            floor_id: cam.floor_id,
            room: cam.room,
            is_active: cam.is_active,
            stream_url: `http://localhost:5000${cam.stream_url}`,
          }));
          this.setCachedData(cacheKey, cameras);
          return cameras;
        }
      }
    } catch (error) {
      console.log('Streaming server not available, trying backend...');
    }

    // Fallback to backend API
    try {
      const response = await fetch(`${API_BASE_URL}/cameras`, {
        headers: this.getAuthHeaders(),
      });
      if (response.ok) {
        const data = await response.json();
        const cameras = data.cameras || data.data || [];
        this.setCachedData(cacheKey, cameras);
        return cameras;
      }
    } catch (error) {
      console.error('Failed to fetch cameras:', error);
    }
    return [];
  }

  async createCamera(camera: Partial<Camera>): Promise<Camera | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/cameras`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(camera),
      });
      if (response.ok) {
        const data = await response.json();
        this.cache.delete('cameras'); // Clear cache
        return data.camera || data.data;
      }
    } catch (error) {
      console.error('Failed to create camera:', error);
    }
    return null;
  }

  async updateCamera(id: number, camera: Partial<Camera>): Promise<Camera | null> {
    try {
      const response = await fetch(`${API_BASE_URL}/cameras/${id}`, {
        method: 'PUT',
        headers: this.getAuthHeaders(),
        body: JSON.stringify(camera),
      });
      if (response.ok) {
        const data = await response.json();
        this.cache.delete('cameras'); // Clear cache
        return data.camera || data.data;
      }
    } catch (error) {
      console.error('Failed to update camera:', error);
    }
    return null;
  }

  async deleteCamera(id: number): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/cameras/${id}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });
      if (response.ok) {
        this.cache.delete('cameras'); // Clear cache
      }
      return response.ok;
    } catch (error) {
      console.error('Failed to delete camera:', error);
      return false;
    }
  }

  // ============ EMPLOYEES ============
  async getEmployees(): Promise<Employee[]> {
    const cacheKey = 'employees';
    const cached = this.getCachedData<Employee[]>(cacheKey);
    if (cached) return cached;

    try {
      console.log('Fetching employees from:', `${API_BASE_URL}/employees`);
      console.log('Using auth headers:', this.getAuthHeaders());
      const response = await fetch(`${API_BASE_URL}/employees`, {
        headers: this.getAuthHeaders(),
      });
      console.log('Employees response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Employees data received:', data);
        const employees = data.employees || data.data || [];
        this.setCachedData(cacheKey, employees);
        return employees;
      } else {
        const errorText = await response.text();
        console.error('Failed to fetch employees - status:', response.status, 'error:', errorText);
      }
    } catch (error) {
      console.error('Failed to fetch employees:', error);
    }
    return [];
  }

  async getEmployeesByFloor(floorId: number): Promise<Employee[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/employees/by-floor/${floorId}`, {
        headers: this.getAuthHeaders(),
      });
      if (response.ok) {
        const data = await response.json();
        return data.employees || data.data || [];
      }
    } catch (error) {
      console.error('Failed to fetch employees by floor:', error);
    }
    return [];
  }

  async deleteEmployee(id: number): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/employees/${id}`, {
        method: 'DELETE',
        headers: this.getAuthHeaders(),
      });
      if (response.ok) {
        this.cache.delete('employees'); // Clear cache
      }
      return response.ok;
    } catch (error) {
      console.error('Failed to delete employee:', error);
      return false;
    }
  }

  // ============ OCCUPANCY ============
  async getFloorOccupancy(floorId: number): Promise<number> {
    try {
      const response = await fetch(`${API_BASE_URL}/presence/floor/${floorId}?count_only=true`, {
        headers: this.getAuthHeaders(),
      });
      if (response.ok) {
        const data = await response.json();
        return data.person_count || 0;
      } else {
        console.error('Failed to fetch floor occupancy. Status:', response.status);
      }
    } catch (error) {
      console.error('Failed to fetch floor occupancy:', error);
    }
    return 0;
  }

  async getAllOccupancy(): Promise<Record<number, number>> {
    const floors = await this.getFloors();
    const occupancy: Record<number, number> = {};
    
    await Promise.all(
      floors.map(async (floor) => {
        occupancy[floor.id] = await this.getFloorOccupancy(floor.id);
      })
    );
    
    return occupancy;
  }

  // ============ ALERTS ============
  async getAlerts(): Promise<any[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts`, {
        headers: this.getAuthHeaders(),
      });
      
      if (response.ok) {
        const data = await response.json();
        // The API returns alerts array directly or in a wrapper
        return data.alerts || data.data || data || [];
      } else {
        console.error('Failed to fetch alerts. Status:', response.status);
      }
    } catch (error) {
      console.error('Failed to fetch alerts:', error);
    }
    return [];
  }

  async getActiveAlerts(): Promise<any[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/active`, {
        headers: this.getAuthHeaders(),
      });
      
      if (response.ok) {
        const data = await response.json();
        return data.data || data.alerts || data || [];
      } else {
        console.error('Failed to fetch active alerts. Status:', response.status);
      }
    } catch (error) {
      console.error('Failed to fetch active alerts:', error);
    }
    return [];
  }

  async acknowledgeAlert(id: number): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/${id}/acknowledge`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });
      
      if (response.ok) {
        this.cache.delete('alerts'); // Clear cache
        return true;
      }
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
    }
    return false;
  }

  async resolveAlert(id: number): Promise<boolean> {
    try {
      const response = await fetch(`${API_BASE_URL}/alerts/${id}/resolve`, {
        method: 'POST',
        headers: this.getAuthHeaders(),
      });
      
      if (response.ok) {
        this.cache.delete('alerts'); // Clear cache
        return true;
      }
    } catch (error) {
      console.error('Failed to resolve alert:', error);
    }
    return false;
  }
}

export const dataService = new DataService();
