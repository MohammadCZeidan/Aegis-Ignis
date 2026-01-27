/**
 * Detection Service API
 * Handles fire detection and face recognition data from Laravel backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

export interface FireDetection {
  cameraId: string;
  confidence: number;
  timestamp: string;
  location: string;
  floorId: string;
}

export interface FaceDetection {
  cameraId: string;
  personName: string;
  confidence: number;
  timestamp: string;
  location: string;
  floorId: string;
  imageUrl?: string;
}

export interface DetectionStats {
  fireDetections: FireDetection[];
  faceDetections: FaceDetection[];
  lastUpdate: string;
}

class DetectionService {
  private fireDetectionInterval: number | null = null;
  private faceDetectionInterval: number | null = null;
  private listeners: ((data: DetectionStats) => void)[] = [];
  private fireServiceOfflineLogged = false;
  private faceServiceOfflineLogged = false;
  private lastAlertedFireIds: Set<string> = new Set();
  
  private currentStats: DetectionStats = {
    fireDetections: [],
    faceDetections: [],
    lastUpdate: new Date().toISOString(),
  };

  private getAuthHeaders(): HeadersInit {
    const token = localStorage.getItem('aegis_auth_token');
    return {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    };
  }

  /**
   * Start fire detection monitoring
   * Checks Laravel backend for recent fire detections (confidence > 25%)
   * Polls every 5 seconds for immediate alerts
   */
  startFireDetection() {
    if (this.fireDetectionInterval) return;
    
    // Run immediately first time
    this.checkFireDetections();
    
    this.fireDetectionInterval = window.setInterval(() => {
      this.checkFireDetections();
    }, 5000); // Check every 5 seconds for immediate fire alerts
  }
  
  private async checkFireDetections() {
    try {
      const response = await fetch(`${API_BASE_URL}/fire-detections`, {
        headers: this.getAuthHeaders(),
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Filter detections with lower threshold (> 25%) from last 5 minutes for better sensitivity
        const recentDetections = (data.fire_detections || data || [])
          .filter((d: any) => {
            const detectionTime = new Date(d.created_at || d.timestamp);
            const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
            return d.confidence > 0.25 && detectionTime > fiveMinutesAgo;
          })
          .map((d: any) => ({
            cameraId: d.camera_id?.toString() || 'Unknown',
            confidence: d.confidence,
            timestamp: d.created_at || d.timestamp,
            location: d.location || `Floor ${d.floor_id || 'Unknown'}`,
            floorId: d.floor_id?.toString() || '1',
          }));
        
        this.currentStats.fireDetections = recentDetections;
        this.currentStats.lastUpdate = new Date().toISOString();
        
        // Trigger alert notification if fire detected
        if (recentDetections.length > 0 && this.hasNewDetections(recentDetections)) {
          this.triggerFireAlert(recentDetections[0]);
        }
        
        this.notifyListeners();
        this.fireServiceOfflineLogged = false;
      }
    } catch (error) {
      // Clear detections if service is unavailable
      if (this.currentStats.fireDetections.length > 0) {
        this.currentStats.fireDetections = [];
        this.notifyListeners();
      }
      
      if (!this.fireServiceOfflineLogged) {
        console.warn('Fire detection backend not available');
        this.fireServiceOfflineLogged = true;
      }
    }
  }

  /**
   * Start face detection monitoring
   * Checks for recent presence logs
   */
  startFaceDetection() {
    if (this.faceDetectionInterval) return;
    
    // Run immediately first time
    this.runFaceDetection();
    
    // Then run every 5 minutes
    this.faceDetectionInterval = window.setInterval(() => {
      this.runFaceDetection();
    }, 5 * 60 * 1000); // 5 minutes
  }

  private async runFaceDetection() {
    try {
      const response = await fetch(`${API_BASE_URL}/presence/people`, {
        headers: this.getAuthHeaders(),
      });
      
      if (response.ok) {
        const data = await response.json();
        
        // Get people detected in last 5 minutes
        const recentDetections = (data.people || data || [])
          .filter((p: any) => {
            const lastSeen = new Date(p.last_seen || p.timestamp);
            const fiveMinutesAgo = new Date(Date.now() - 5 * 60 * 1000);
            return lastSeen > fiveMinutesAgo;
          })
          .map((p: any) => ({
            cameraId: p.camera_id?.toString() || 'Unknown',
            personName: p.employee_name || p.name || 'Unknown Person',
            confidence: p.confidence || 0.9,
            timestamp: p.last_seen || p.timestamp,
            location: p.location || `Floor ${p.floor_id || 'Unknown'}`,
            floorId: p.floor_id?.toString() || '1',
            imageUrl: p.photo_url,
          }));
        
        this.currentStats.faceDetections = recentDetections;
        this.currentStats.lastUpdate = new Date().toISOString();
        this.notifyListeners();
        this.faceServiceOfflineLogged = false;
      }
    } catch (error) {
      if (!this.faceServiceOfflineLogged) {
        console.warn('Face detection backend not available');
        this.faceServiceOfflineLogged = true;
      }
    }
  }

  /**
   * Stop all detection monitoring
   */
  stopAllDetection() {
    if (this.fireDetectionInterval) {
      clearInterval(this.fireDetectionInterval);
      this.fireDetectionInterval = null;
    }
    
    if (this.faceDetectionInterval) {
      clearInterval(this.faceDetectionInterval);
      this.faceDetectionInterval = null;
    }
  }

  /**
   * Subscribe to detection updates
   */
  subscribe(callback: (data: DetectionStats) => void) {
    this.listeners.push(callback);
    // Send current stats immediately
    callback(this.currentStats);
    
    return () => {
      this.listeners = this.listeners.filter(l => l !== callback);
    };
  }

  private notifyListeners() {
    this.listeners.forEach(listener => listener(this.currentStats));
  }

  /**
   * Check if there are new fire detections we haven't alerted about
   */
  private hasNewDetections(detections: FireDetection[]): boolean {
    return detections.some(d => {
      const detectionId = `${d.cameraId}-${d.timestamp}`;
      return !this.lastAlertedFireIds.has(detectionId);
    });
  }

  /**
   * Trigger fire alert notification
   */
  private async triggerFireAlert(detection: FireDetection) {
    const detectionId = `${detection.cameraId}-${detection.timestamp}`;
    
    // Avoid duplicate alerts
    if (this.lastAlertedFireIds.has(detectionId)) {
      return;
    }
    
    this.lastAlertedFireIds.add(detectionId);
    
    // Clean up old IDs (keep last 50)
    if (this.lastAlertedFireIds.size > 50) {
      const idsArray = Array.from(this.lastAlertedFireIds);
      this.lastAlertedFireIds = new Set(idsArray.slice(-50));
    }
    
    // Import notification service dynamically to avoid circular dependencies
    try {
      const { notificationService } = await import('./notificationService');
      
      // Show critical alert
      notificationService.error(
        `FIRE DETECTED! ${detection.location} - ${Math.round(detection.confidence * 100)}% confidence`,
        10000 // Show for 10 seconds
      );
      
      // Play alert sound if available
      this.playAlertSound();
      
      console.error('FIRE ALERT', {
        location: detection.location,
        camera: detection.cameraId,
        confidence: `${Math.round(detection.confidence * 100)}%`,
        timestamp: detection.timestamp,
      });
    } catch (error) {
      console.error('Failed to show fire alert notification:', error);
    }
  }

  /**
   * Play alert sound for fire detection
   */
  private playAlertSound() {
    try {
      // Create audio context for alert beep
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();
      
      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      oscillator.frequency.value = 800; // 800 Hz beep
      oscillator.type = 'sine';
      
      gainNode.gain.setValueAtTime(0.3, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
      
      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.5);
      
      // Second beep
      setTimeout(() => {
        const osc2 = audioContext.createOscillator();
        const gain2 = audioContext.createGain();
        
        osc2.connect(gain2);
        gain2.connect(audioContext.destination);
        
        osc2.frequency.value = 1000;
        osc2.type = 'sine';
        
        gain2.gain.setValueAtTime(0.3, audioContext.currentTime);
        gain2.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.5);
        
        osc2.start(audioContext.currentTime);
        osc2.stop(audioContext.currentTime + 0.5);
      }, 300);
    } catch (error) {
      console.warn('Could not play alert sound:', error);
    }
  }

  /**
   * Get current detection stats
   */
  getCurrentStats(): DetectionStats {
    return this.currentStats;
  }

  /**
   * Manually trigger face detection now
   */
  async triggerFaceDetection() {
    await this.runFaceDetection();
  }

  /**
   * Clear old detections
   */
  clearDetections() {
    this.currentStats = {
      fireDetections: [],
      faceDetections: [],
      lastUpdate: new Date().toISOString(),
    };
    this.notifyListeners();
  }
}

export const detectionService = new DetectionService();
