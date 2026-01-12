// Mock data for the Smart Building Security & Fire Detection System

export interface Camera {
  id: string;
  name: string;
  location: string;
  floorId: string;
  status: 'online' | 'offline';
  rtspUrl: string;
  detections: Detection[];
}

export interface Detection {
  id: string;
  type: 'fire' | 'smoke' | 'person';
  cameraId: string;
  timestamp: Date;
  confidence: number;
  trackId?: string;
  personName?: string;
}

export interface Floor {
  id: string;
  name: string;
  number: number;
  occupancy: number;
  maxOccupancy: number;
  status: 'normal' | 'warning' | 'critical';
  cameras: string[];
}

export interface Alert {
  id: string;
  type: 'fire' | 'smoke' | 'security';
  floorId: string;
  cameraId: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  timestamp: Date;
  status: 'active' | 'acknowledged' | 'resolved';
  message: string;
  emergencyCallStatus?: 'pending' | 'connected' | 'failed';
}

export interface Person {
  id: string;
  name: string;
  trackId: string;
  lastSeen: Date;
  floorId: string;
  avatar?: string;
}

export const floors: Floor[] = [
  {
    id: 'floor-1',
    name: 'Ground Floor',
    number: 1,
    occupancy: 24,
    maxOccupancy: 50,
    status: 'normal',
    cameras: ['1', '2', '3', '4']
  },
  {
    id: 'floor-2',
    name: 'Second Floor',
    number: 2,
    occupancy: 18,
    maxOccupancy: 40,
    status: 'normal',
    cameras: ['5', '6', '7', '8']
  },
  {
    id: 'floor-3',
    name: 'Third Floor',
    number: 3,
    occupancy: 32,
    maxOccupancy: 40,
    status: 'warning',
    cameras: ['9', '10', '11', '12']
  },
  {
    id: 'floor-4',
    name: 'Fourth Floor',
    number: 4,
    occupancy: 5,
    maxOccupancy: 30,
    status: 'critical',
    cameras: ['13', '14', '15']
  }
];

export const cameras: Camera[] = [
  // Ground Floor
  { id: '1', name: 'Main Webcam', location: 'Office', floorId: 'floor-1', status: 'online', rtspUrl: '0', detections: [] },
  { id: '2', name: 'Reception Area', location: 'Reception', floorId: 'floor-1', status: 'offline', rtspUrl: 'rtsp://cam2', detections: [] },
  { id: '3', name: 'Corridor A', location: 'East Corridor', floorId: 'floor-1', status: 'offline', rtspUrl: 'rtsp://cam3', detections: [] },
  { id: '4', name: 'Emergency Exit', location: 'Back Exit', floorId: 'floor-1', status: 'offline', rtspUrl: 'rtsp://cam4', detections: [] },
  
  // Second Floor
  { id: '5', name: 'Conference Room A', location: 'Meeting Area', floorId: 'floor-2', status: 'offline', rtspUrl: 'rtsp://cam5', detections: [] },
  { id: '6', name: 'Open Workspace', location: 'North Wing', floorId: 'floor-2', status: 'offline', rtspUrl: 'rtsp://cam6', detections: [] },
  { id: '7', name: 'Break Room', location: 'Central', floorId: 'floor-2', status: 'offline', rtspUrl: 'rtsp://cam7', detections: [] },
  { id: '8', name: 'Server Room', location: 'South Wing', floorId: 'floor-2', status: 'offline', rtspUrl: 'rtsp://cam8', detections: [] },
  
  // Third Floor
  { id: '9', name: 'Executive Office', location: 'Corner Office', floorId: 'floor-3', status: 'offline', rtspUrl: 'rtsp://cam9', detections: [] },
  { id: '10', name: 'Hallway B', location: 'Main Corridor', floorId: 'floor-3', status: 'offline', rtspUrl: 'rtsp://cam10', detections: [] },
  { id: '11', name: 'Storage Room', location: 'West Wing', floorId: 'floor-3', status: 'offline', rtspUrl: 'rtsp://cam11', detections: [] },
  { id: '12', name: 'Stairwell Access', location: 'Emergency Stairs', floorId: 'floor-3', status: 'offline', rtspUrl: 'rtsp://cam12', detections: [] },
  
  // Fourth Floor
  { id: '13', name: 'Data Center', location: 'North Section', floorId: 'floor-4', status: 'offline', rtspUrl: 'rtsp://cam13', detections: [] },
  { id: '14', name: 'Maintenance Area', location: 'South Section', floorId: 'floor-4', status: 'offline', rtspUrl: 'rtsp://cam14', detections: [] },
  { id: '15', name: 'Roof Access', location: 'Stairwell', floorId: 'floor-4', status: 'offline', rtspUrl: 'rtsp://cam15', detections: [] }
];

export const alerts: Alert[] = [
  {
    id: 'alert-1',
    type: 'fire',
    floorId: 'floor-4',
    cameraId: '13',
    severity: 'critical',
    timestamp: new Date(Date.now() - 5 * 60 * 1000), // 5 minutes ago
    status: 'active',
    message: 'Fire detected in Data Center',
    emergencyCallStatus: 'connected'
  },
  {
    id: 'alert-2',
    type: 'smoke',
    floorId: 'floor-3',
    cameraId: '11',
    severity: 'high',
    timestamp: new Date(Date.now() - 15 * 60 * 1000), // 15 minutes ago
    status: 'acknowledged',
    message: 'Smoke detected in Storage Room'
  },
  {
    id: 'alert-3',
    type: 'security',
    floorId: 'floor-1',
    cameraId: '4',
    severity: 'medium',
    timestamp: new Date(Date.now() - 45 * 60 * 1000), // 45 minutes ago
    status: 'resolved',
    message: 'Unauthorized access attempt at Emergency Exit'
  }
];

export const people: Person[] = [
  { id: 'p1', name: 'John Smith', trackId: 'TRK001', lastSeen: new Date(), floorId: 'floor-1', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John' },
  { id: 'p2', name: 'Sarah Johnson', trackId: 'TRK002', lastSeen: new Date(Date.now() - 2 * 60 * 1000), floorId: 'floor-2', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah' },
  { id: 'p3', name: 'Unknown Person', trackId: 'TRK003', lastSeen: new Date(Date.now() - 5 * 60 * 1000), floorId: 'floor-1' },
  { id: 'p4', name: 'Michael Chen', trackId: 'TRK004', lastSeen: new Date(Date.now() - 8 * 60 * 1000), floorId: 'floor-3', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Michael' },
  { id: 'p5', name: 'Emma Davis', trackId: 'TRK005', lastSeen: new Date(), floorId: 'floor-2', avatar: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Emma' },
];

// Occupancy data for the last 24 hours
export const occupancyData = [
  { time: '00:00', count: 2 },
  { time: '02:00', count: 1 },
  { time: '04:00', count: 3 },
  { time: '06:00', count: 8 },
  { time: '08:00', count: 45 },
  { time: '10:00', count: 68 },
  { time: '12:00', count: 72 },
  { time: '14:00', count: 65 },
  { time: '16:00', count: 58 },
  { time: '18:00', count: 32 },
  { time: '20:00', count: 15 },
  { time: '22:00', count: 5 },
  { time: '23:59', count: 79 }
];

export const getFloorById = (id: string) => floors.find(f => f.id === id);
export const getCameraById = (id: string) => cameras.find(c => c.id === id);
export const getAlertById = (id: string) => alerts.find(a => a.id === id);
export const getCamerasByFloor = (floorId: string) => cameras.filter(c => c.floorId === floorId);
export const getPeopleByFloor = (floorId: string) => people.filter(p => p.floorId === floorId);
export const getActiveAlerts = () => alerts.filter(a => a.status === 'active');
