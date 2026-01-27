const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export { API_BASE_URL };

interface Floor {
  id: number;
  floor_number: number;
  name: string | null;
}

interface Employee {
  id: number;
  name: string;
  email: string | null;
  floor_id: number | null;
  floor_name: string | null;
  photo_url: string | null;
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
    const headers: HeadersInit = {};
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
        credentials: 'include', // Include credentials for CORS
        headers: {
          ...this.getAuthHeaders(),
          ...options?.headers,
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('aegis_auth_token');
          localStorage.removeItem('aegis_user');
          window.location.href = '/';
          throw new Error('Unauthorized');
        }

        if (response.status === 429) {
          const retryAfter = response.headers.get('Retry-After');
          const delay = retryAfter ? parseInt(retryAfter) * 1000 : this.retryDelay;
          
          if (retryCount < this.maxRetries) {
            console.warn(`Rate limited. Retrying after ${delay}ms...`);
            await this.sleep(delay);
            return this.request<T>(endpoint, options, retryCount + 1);
          }
        }

        const error = await response.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(error.detail || error.message || 'Request failed');
      }

      return response.json();
      
    } catch (error) {
      // Retry on network errors
      if (retryCount < this.maxRetries && error instanceof TypeError) {
        console.warn(`Network error. Retrying (${retryCount + 1}/${this.maxRetries})...`);
        await this.sleep(this.retryDelay * (retryCount + 1));
        return this.request<T>(endpoint, options, retryCount + 1);
      }
      throw error;
    }
  }

  async getFloors(): Promise<Floor[]> {
    return this.request<Floor[]>('/floors');
  }

  async getEmployees(floorId?: number): Promise<{ employees: Employee[]; total: number }> {
    const params = floorId ? `?floor_id=${floorId}` : '';
    return this.request(`/employees${params}`);
  }

  async registerEmployee(formData: FormData, retryCount: number = 0): Promise<Employee> {
    const token = localStorage.getItem('aegis_auth_token');
    
    try {
      const response = await fetch(`${this.baseUrl}/employees/register-face`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });

      if (!response.ok) {
        if (response.status === 401) {
          localStorage.removeItem('aegis_auth_token');
          localStorage.removeItem('aegis_user');
          window.location.href = '/';
          throw new Error('Unauthorized');
        }

        const error = await response.json().catch(() => ({ detail: 'Registration failed' }));
        throw new Error(error.detail || error.message || 'Registration failed');
      }

      return response.json();
      
    } catch (error) {
      // Retry on network errors
      if (retryCount < this.maxRetries && error instanceof TypeError) {
        console.warn(`Network error during registration. Retrying (${retryCount + 1}/${this.maxRetries})...`);
        await this.sleep(this.retryDelay * (retryCount + 1));
        return this.registerEmployee(formData, retryCount + 1);
      }
      throw error;
    }
  }

  async healthCheck(): Promise<{ status: string }> {
    return this.request('/health');
  }
}

export const api = new ApiClient();

