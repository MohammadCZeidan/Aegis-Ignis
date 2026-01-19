/**
 * Employee Service API
 * Handles employee data and face registration
 */

const BACKEND_API = import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1';

export interface Employee {
  id: string;
  name: string;
  email: string;
  role: string;
  department: string;
  floorId?: string;
  imageUrl?: string;
  lastSeen?: string;
  location?: string;
}

class EmployeeService {
  /**
   * Get all registered employees
   */
  async getAllEmployees(): Promise<Employee[]> {
    try {
      const response = await fetch(`${BACKEND_API}/employees`);
      if (response.ok) {
        const data = await response.json();
        return data.employees || [];
      }
    } catch (error) {
      console.error('Failed to fetch employees:', error);
    }
    
    // Return mock data if API fails
    return this.getMockEmployees();
  }

  /**
   * Get employees by floor
   */
  async getEmployeesByFloor(floorId: string): Promise<Employee[]> {
    try {
      const response = await fetch(`${BACKEND_API}/employees/floor/${floorId}`);
      if (response.ok) {
        const data = await response.json();
        return data.employees || [];
      }
    } catch (error) {
      console.error('Failed to fetch employees by floor:', error);
    }
    
    // Filter mock data by floor
    const allEmployees = this.getMockEmployees();
    return allEmployees.filter(emp => emp.floorId === floorId);
  }

  /**
   * Get employees currently present on a floor
   */
  async getPresentEmployees(floorId: string): Promise<Employee[]> {
    try {
      const response = await fetch(`${BACKEND_API}/presence/floor/${floorId}`);
      if (response.ok) {
        const data = await response.json();
        return data.present || [];
      }
    } catch (error) {
      console.error('Failed to fetch present employees:', error);
    }
    
    return [];
  }

  /**
   * Mock employee data for development
   */
  private getMockEmployees(): Employee[] {
    return [
      {
        id: '1',
        name: 'John Smith',
        email: 'john.smith@company.com',
        role: 'Security Manager',
        department: 'Security',
        floorId: '1',
        imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John',
        lastSeen: new Date(Date.now() - 1000 * 60 * 15).toISOString(),
        location: 'Main Lobby'
      },
      {
        id: '2',
        name: 'Sarah Johnson',
        email: 'sarah.j@company.com',
        role: 'Office Manager',
        department: 'Administration',
        floorId: '2',
        imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah',
        lastSeen: new Date(Date.now() - 1000 * 60 * 5).toISOString(),
        location: 'Conference Room A'
      },
      {
        id: '3',
        name: 'Michael Chen',
        email: 'michael.chen@company.com',
        role: 'IT Specialist',
        department: 'IT',
        floorId: '3',
        imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Michael',
        lastSeen: new Date(Date.now() - 1000 * 60 * 2).toISOString(),
        location: 'Server Room'
      },
      {
        id: '4',
        name: 'Emily Davis',
        email: 'emily.d@company.com',
        role: 'HR Manager',
        department: 'Human Resources',
        floorId: '2',
        imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Emily',
        lastSeen: new Date(Date.now() - 1000 * 60 * 30).toISOString(),
        location: 'HR Office'
      },
      {
        id: '5',
        name: 'David Wilson',
        email: 'david.w@company.com',
        role: 'Facilities Manager',
        department: 'Facilities',
        floorId: '1',
        imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=David',
        lastSeen: new Date(Date.now() - 1000 * 60 * 10).toISOString(),
        location: 'Maintenance Area'
      },
      {
        id: '6',
        name: 'Lisa Anderson',
        email: 'lisa.a@company.com',
        role: 'Executive Assistant',
        department: 'Executive',
        floorId: '4',
        imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Lisa',
        lastSeen: new Date(Date.now() - 1000 * 60 * 7).toISOString(),
        location: 'Executive Suite'
      },
      {
        id: '7',
        name: 'Robert Martinez',
        email: 'robert.m@company.com',
        role: 'Data Analyst',
        department: 'Analytics',
        floorId: '3',
        imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Robert',
        lastSeen: new Date(Date.now() - 1000 * 60 * 45).toISOString(),
        location: 'Analytics Lab'
      },
      {
        id: '8',
        name: 'Jennifer Lee',
        email: 'jennifer.l@company.com',
        role: 'Marketing Director',
        department: 'Marketing',
        floorId: '2',
        imageUrl: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Jennifer',
        lastSeen: new Date(Date.now() - 1000 * 60 * 20).toISOString(),
        location: 'Marketing Department'
      }
    ];
  }

  /**
   * Format time ago from timestamp
   */
  getTimeAgo(timestamp: string): string {
    const now = new Date();
    const then = new Date(timestamp);
    const diffMs = now.getTime() - then.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    
    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins} min ago`;
    
    const diffHours = Math.floor(diffMins / 60);
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    
    const diffDays = Math.floor(diffHours / 24);
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  }
}

export const employeeService = new EmployeeService();
