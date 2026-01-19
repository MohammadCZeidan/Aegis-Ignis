// API Configuration
// All API endpoints are configured here using environment variables

export const API_CONFIG = {
  // Laravel Backend API
  BACKEND_API: import.meta.env.VITE_BACKEND_API_URL || 'http://localhost:8000/api/v1',
  
  // Python Services
  FACE_SERVICE: import.meta.env.VITE_FACE_SERVICE_URL || 'http://localhost:8001',
  FIRE_SERVICE: import.meta.env.VITE_FIRE_SERVICE_URL || 'http://localhost:8002',
  FLOOR_SERVICE: import.meta.env.VITE_FLOOR_SERVICE_URL || 'http://localhost:8003',
  CAMERA_SERVICE: import.meta.env.VITE_CAMERA_SERVICE_URL || 'http://localhost:5000',
  
  // Face Registration App
  FACE_REGISTRATION: import.meta.env.VITE_FACE_REGISTRATION_URL || 'http://localhost:5174',
} as const;

// Helper functions for building API URLs
export const buildBackendUrl = (path: string) => `${API_CONFIG.BACKEND_API}${path}`;
export const buildFaceServiceUrl = (path: string) => `${API_CONFIG.FACE_SERVICE}${path}`;
export const buildFireServiceUrl = (path: string) => `${API_CONFIG.FIRE_SERVICE}${path}`;
export const buildFloorServiceUrl = (path: string) => `${API_CONFIG.FLOOR_SERVICE}${path}`;
export const buildCameraServiceUrl = (path: string) => `${API_CONFIG.CAMERA_SERVICE}${path}`;

// Storage URL helper (for images from Laravel backend)
export const getStorageUrl = (path: string) => {
  const baseUrl = API_CONFIG.BACKEND_API.replace('/api/v1', '');
  return `${baseUrl}/storage/${path}`;
};
