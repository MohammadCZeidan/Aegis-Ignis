import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Camera, Flame, Users, AlertCircle, Play, Pause, RefreshCw } from 'lucide-react';
import { API_CONFIG, buildBackendUrl } from '../../config/api';

interface CameraFeed {
  id: string;
  name: string;
  floor_id: number;
  floor_name: string;
  room_location: string;
  status: 'online' | 'offline';
  stream_url?: string;
}
interface Detection {
  type: 'fire' | 'face';
  confidence: number;
  name?: string;
  timestamp: string;
  bbox?: number[];
}

export default function LiveCameraView() {
  const [cameras, setCameras] = useState<CameraFeed[]>([]);
  const [selectedCamera, setSelectedCamera] = useState<CameraFeed | null>(null);
  const [detections, setDetections] = useState<Detection[]>([]);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const detectionInterval = useRef<number | null>(null);

  // Fetch cameras
  useEffect(() => {
    fetchCameras();
  }, []);

  const fetchCameras = async () => {
    try {
      const response = await fetch(buildBackendUrl('/cameras'), {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('aegis_auth_token')}`,
        },
      });
      if (response.ok) {
        const data = await response.json();
        setCameras(data.cameras || []);
        if (data.cameras?.length > 0 && !selectedCamera) {
          setSelectedCamera(data.cameras[0]);
        }
      }
    } catch (error) {
      console.error('Error fetching cameras:', error);
    }
  };

  // Start monitoring
  const startMonitoring = async () => {
    if (!selectedCamera) return;

    setIsMonitoring(true);

    // If we have a stream URL, use it
    if (selectedCamera.stream_url) {
      if (videoRef.current) {
        videoRef.current.src = selectedCamera.stream_url;
        videoRef.current.play();
      }
    } else {
      // Use webcam
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
      } catch (err) {
        console.error('Error accessing webcam:', err);
      }
    }

    // Start detection loop
    detectionInterval.current = window.setInterval(() => {
      captureAndDetect();
    }, 2000); // Every 2 seconds
  };

  // Stop monitoring
  const stopMonitoring = () => {
    setIsMonitoring(false);

    if (detectionInterval.current) {
      clearInterval(detectionInterval.current);
      detectionInterval.current = null;
    }

    if (videoRef.current?.srcObject) {
      const stream = videoRef.current.srcObject as MediaStream;
      stream.getTracks().forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
  };

  // Capture frame and run detection
  const captureAndDetect = async () => {
    if (!videoRef.current || !canvasRef.current) return;

    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw current frame
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Convert to blob
    canvas.toBlob(async (blob) => {
      if (!blob) return;

      // Run fire detection
      await detectFire(blob);

      // Run face detection
      await detectFaces(blob);
    }, 'image/jpeg', 0.85);
  };

  // Detect fire
  const detectFire = async (imageBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('file', imageBlob, 'frame.jpg');

      const response = await fetch(`${API_CONFIG.FIRE_SERVICE}/detect-fire`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        if (result.detected && result.confidence >= 0.3) {
          const newDetection: Detection = {
            type: 'fire',
            confidence: result.confidence,
            timestamp: new Date().toISOString(),
            bbox: result.bounding_box,
          };
          setDetections(prev => [newDetection, ...prev].slice(0, 10));
        }
      }
    } catch (error) {
      console.error('Fire detection error:', error);
    }
  };

  // Detect faces
  const detectFaces = async (imageBlob: Blob) => {
    try {
      const formData = new FormData();
      formData.append('file', imageBlob, 'frame.jpg');

      const response = await fetch(`${API_CONFIG.FACE_SERVICE}/detect-faces`, {
        method: 'POST',
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        const faces = result.faces || [];

        // Identify each face
        for (const face of faces) {
          if (!face.embedding) continue;

          try {
            const identifyResponse = await fetch(buildBackendUrl('/employees/identify-face'), {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ embedding: face.embedding }),
            });

            if (identifyResponse.ok) {
              const person = await identifyResponse.json();
              if (person.matched) {
                const newDetection: Detection = {
                  type: 'face',
                  confidence: person.confidence,
                  name: person.name,
                  timestamp: new Date().toISOString(),
                  bbox: face.bbox,
                };
                setDetections(prev => [newDetection, ...prev].slice(0, 10));
              }
            }
          } catch (err) {
            console.error('Face identification error:', err);
          }
        }
      }
    } catch (error) {
      console.error('Face detection error:', error);
    }
  };

  useEffect(() => {
    return () => {
      stopMonitoring();
    };
  }, []);

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Live Camera Monitoring</h1>
          <p className="text-muted-foreground">Real-time fire and face detection</p>
        </div>
        <Button onClick={fetchCameras} variant="outline" size="sm">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Camera List */}
        <Card>
          <CardHeader>
            <CardTitle>Available Cameras</CardTitle>
            <CardDescription>{cameras.length} cameras found</CardDescription>
          </CardHeader>
          <CardContent className="space-y-2">
            {cameras.map((camera) => (
              <button
                key={camera.id}
                onClick={() => {
                  stopMonitoring();
                  setSelectedCamera(camera);
                  setDetections([]);
                }}
                className={`w-full p-3 rounded-lg border text-left transition-colors ${
                  selectedCamera?.id === camera.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Camera className="h-4 w-4" />
                    <span className="font-medium">{camera.name}</span>
                  </div>
                  <Badge variant={camera.status === 'online' ? 'default' : 'secondary'}>
                    {camera.status}
                  </Badge>
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {camera.floor_name} • {camera.room_location}
                </p>
              </button>
            ))}
          </CardContent>
        </Card>

        {/* Live Feed */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>
                  {selectedCamera ? selectedCamera.name : 'No Camera Selected'}
                </CardTitle>
                <CardDescription>
                  {selectedCamera
                    ? `${selectedCamera.floor_name} • ${selectedCamera.room_location}`
                    : 'Select a camera to start monitoring'}
                </CardDescription>
              </div>
              {selectedCamera && (
                <Button
                  onClick={isMonitoring ? stopMonitoring : startMonitoring}
                  variant={isMonitoring ? 'destructive' : 'default'}
                >
                  {isMonitoring ? (
                    <>
                      <Pause className="h-4 w-4 mr-2" />
                      Stop
                    </>
                  ) : (
                    <>
                      <Play className="h-4 w-4 mr-2" />
                      Start
                    </>
                  )}
                </Button>
              )}
            </div>
          </CardHeader>
          <CardContent>
            <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
              <video
                ref={videoRef}
                className="w-full h-full object-contain"
                autoPlay
                playsInline
                muted
              />
              <canvas ref={canvasRef} className="hidden" />

              {!isMonitoring && (
                <div className="absolute inset-0 flex items-center justify-center bg-black/50">
                  <div className="text-center text-white">
                    <Camera className="h-12 w-12 mx-auto mb-2 opacity-50" />
                    <p>Camera feed inactive</p>
                  </div>
                </div>
              )}

              {isMonitoring && (
                <div className="absolute top-4 right-4">
                  <Badge variant="destructive" className="animate-pulse">
                    ● LIVE
                  </Badge>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Detection Log */}
        <Card className="lg:col-span-3">
          <CardHeader>
            <CardTitle>Recent Detections</CardTitle>
            <CardDescription>Last 10 detections from camera feed</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {detections.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-8">
                  No detections yet. Start monitoring to see detections.
                </p>
              ) : (
                detections.map((detection, index) => (
                  <div
                    key={index}
                    className={`p-3 rounded-lg border ${
                      detection.type === 'fire'
                        ? 'border-red-200 bg-red-50'
                        : 'border-blue-200 bg-blue-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        {detection.type === 'fire' ? (
                          <Flame className="h-4 w-4 text-red-600" />
                        ) : (
                          <Users className="h-4 w-4 text-blue-600" />
                        )}
                        <span className="font-medium">
                          {detection.type === 'fire' ? 'Fire Detected' : detection.name || 'Person Detected'}
                        </span>
                      </div>
                      <Badge variant={detection.type === 'fire' ? 'destructive' : 'default'}>
                        {Math.round(detection.confidence * 100)}% confidence
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {new Date(detection.timestamp).toLocaleTimeString()}
                    </p>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Info Banner */}
      <Card className="border-blue-200 bg-blue-50">
        <CardContent className="pt-6">
          <div className="flex gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="text-sm font-medium text-blue-900">
                How Presence Tracking Works
              </p>
              <p className="text-sm text-blue-700">
                When the camera detects a person, they're tracked on this floor for 5 minutes. 
                If the camera sees them again within 5 minutes, the timer resets. After 5 minutes 
                without detection, they're removed from the floor occupancy.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
