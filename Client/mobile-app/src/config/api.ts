// API Configuration for React Native
// Uses environment variables from .env file

import {BACKEND_API_URL, FACE_SERVICE_URL, FIRE_SERVICE_URL, FLOOR_SERVICE_URL, CAMERA_SERVICE_URL} from '@env';
import {Platform} from 'react-native';

// Get API URL from environment or use defaults
const getBackendApiUrl = (): string => {
  // Priority: .env file > Platform-specific defaults
  if (BACKEND_API_URL) {
    return BACKEND_API_URL;
  }

  // Fallback defaults based on platform
  if (__DEV__) {
    // Development mode
    const host = Platform.OS === 'android' ? '10.0.2.2' : 'localhost';
    return `http://${host}:8000/api/v1`;
  }

  // Production fallback (should be set in .env)
  return 'http://35.180.227.44/api/v1';
};

const getServiceUrl = (envValue: string | undefined, defaultPort: number): string => {
  if (envValue) {
    return envValue;
  }

  // Fallback to local development
  if (__DEV__) {
    const host = Platform.OS === 'android' ? '10.0.2.2' : 'localhost';
    return `http://${host}:${defaultPort}`;
  }

  // Production fallback
  return `http://35.180.227.44:${defaultPort}`;
};

export const API_CONFIG = {
  BACKEND_API: getBackendApiUrl(),
  FACE_SERVICE: getServiceUrl(FACE_SERVICE_URL, 8001),
  FIRE_SERVICE: getServiceUrl(FIRE_SERVICE_URL, 8002),
  FLOOR_SERVICE: getServiceUrl(FLOOR_SERVICE_URL, 8003),
  CAMERA_SERVICE: getServiceUrl(CAMERA_SERVICE_URL, 5000),
} as const;

export const buildBackendUrl = (path: string) => `${API_CONFIG.BACKEND_API}${path}`;
export const buildFaceServiceUrl = (path: string) => `${API_CONFIG.FACE_SERVICE}${path}`;
export const buildFireServiceUrl = (path: string) => `${API_CONFIG.FIRE_SERVICE}${path}`;
export const buildFloorServiceUrl = (path: string) => `${API_CONFIG.FLOOR_SERVICE}${path}`;
export const buildCameraServiceUrl = (path: string) => `${API_CONFIG.CAMERA_SERVICE}${path}`;

export const getStorageUrl = (path: string) => {
  const baseUrl = API_CONFIG.BACKEND_API.replace('/api/v1', '');
  return `${baseUrl}/storage/${path}`;
};
