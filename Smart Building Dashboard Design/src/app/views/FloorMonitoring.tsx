import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { dataService, type Employee } from '../services/dataService';

interface FloorData {
  id: number;
  name: string;
  level: number;
}

interface FireDetection {
  id: number;
  camera_id: number;
  floor_id: number;
  detected_at: string;
  event_type: string;
  fire_type?: string;
  severity: string;
  confidence: number;
  resolved: boolean;
  screenshot_path?: string;
  room?: string;
}

interface PresenceRecord {
  employee_id: number;
  employee_name: string;
  floor_id: number;
  room_location: string;
  last_seen_at: string;
  confidence: number;
  face_photo_path?: string;
}

export default function FloorMonitoring() {
  const [floors, setFloors] = useState<FloorData[]>([]);
  const [selectedFloor, setSelectedFloor] = useState<number | null>(null);
  const [presence, setPresence] = useState<PresenceRecord[]>([]);
  const [fireDetections, setFireDetections] = useState<FireDetection[]>([]);
  const [loading, setLoading] = useState(true);

  // Load floors
  useEffect(() => {
    const loadFloors = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/floors');
        const data = await response.json();
        setFloors(data);
        if (data.length > 0 && !selectedFloor) {
          setSelectedFloor(data[0].id);
        }
      } catch (error) {
        console.error('Failed to load floors:', error);
      } finally {
        setLoading(false);
      }
    };
    loadFloors();
  }, []);

  // Load presence data for selected floor
  useEffect(() => {
    if (!selectedFloor) return;

    const loadFloorData = async () => {
      try {
        // Get presence data
        const presenceResponse = await fetch(
          `http://localhost:8000/api/v1/presence/floor/${selectedFloor}`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
          }
        );
        const presenceData = await presenceResponse.json();
        setPresence(presenceData);

        // Get fire detections from alerts endpoint
        const fireResponse = await fetch(
          `http://localhost:8000/api/v1/alerts/by-floor/${selectedFloor}`,
          {
            headers: {
              'Authorization': `Bearer ${localStorage.getItem('token')}`,
            },
          }
        );
        const fireData = await fireResponse.json();
        // Filter only fire-related alerts
        const fireAlerts = fireData.filter((alert: any) => 
          alert.event_type === 'fire' || alert.event_type === 'fire_detection'
        );
        setFireDetections(fireAlerts);
      } catch (error) {
        console.error('Failed to load floor data:', error);
      }
    };

    loadFloorData();
    const interval = setInterval(loadFloorData, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [selectedFloor]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-500 text-white';
      case 'alert':
        return 'bg-orange-500 text-white';
      case 'warning':
        return 'bg-yellow-500 text-black';
      default:
        return 'bg-gray-500 text-white';
    }
  };

  const getTimeSince = (dateString: string) => {
    const date = new Date(dateString);
    const seconds = Math.floor((Date.now() - date.getTime()) / 1000);
    
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const currentFloor = floors.find(f => f.id === selectedFloor);

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading floor data...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Floor Monitoring</h1>
          <p className="text-gray-600 mt-1">Real-time presence and detection tracking</p>
        </div>
        <Badge variant="outline" className="text-sm">
          Auto-refresh: 5s
        </Badge>
      </div>

      {/* Floor Selector */}
      <Card>
        <CardHeader>
          <CardTitle>Select Floor</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2 flex-wrap">
            <Button
              variant={selectedFloor === null ? 'default' : 'outline'}
              onClick={() => setSelectedFloor(null)}
            >
              All Floors
            </Button>
            {floors.map((floor) => (
              <Button
                key={floor.id}
                variant={selectedFloor === floor.id ? 'default' : 'outline'}
                onClick={() => setSelectedFloor(floor.id)}
              >
                {floor.name}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {currentFloor && (
        <>
          {/* People Present on Floor */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>People on {currentFloor.name}</CardTitle>
                <Badge className="text-lg">
                  {presence.length} {presence.length === 1 ? 'person' : 'people'}
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {presence.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p className="text-lg">No one detected on this floor</p>
                  <p className="text-sm mt-2">People will appear here when detected by cameras</p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {presence.map((person, index) => (
                    <Card key={index} className="border-2">
                      <CardContent className="p-4">
                        <div className="flex items-start gap-3">
                          {/* Face Photo */}
                          {person.face_photo_path ? (
                            <img
                              src={`http://localhost:8000/storage/${person.face_photo_path}`}
                              alt={person.employee_name}
                              className="w-16 h-16 rounded-full object-cover border-2 border-blue-500"
                              onError={(e) => {
                                e.currentTarget.src = 'data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" fill="%23ddd"/><text x="50%" y="50%" text-anchor="middle" dy=".3em" fill="%23999" font-size="20">?</text></svg>';
                              }}
                            />
                          ) : (
                            <div className="w-16 h-16 rounded-full bg-gray-200 flex items-center justify-center text-2xl font-bold text-gray-500">
                              {person.employee_name.charAt(0).toUpperCase()}
                            </div>
                          )}

                          {/* Person Info */}
                          <div className="flex-1 min-w-0">
                            <h3 className="font-semibold text-gray-900 truncate">
                              {person.employee_name}
                            </h3>
                            <p className="text-sm text-gray-600">
                              📍 {person.room_location}
                            </p>
                            <div className="flex items-center gap-2 mt-2">
                              <Badge variant="outline" className="text-xs">
                                {Math.round(person.confidence * 100)}% match
                              </Badge>
                              <span className="text-xs text-gray-500">
                                {getTimeSince(person.last_seen_at)}
                              </span>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Fire Detections on Floor */}
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Fire Detections on {currentFloor.name}</CardTitle>
                <Badge variant="destructive" className="text-lg">
                  {fireDetections.filter(f => !f.resolved).length} active
                </Badge>
              </div>
            </CardHeader>
            <CardContent>
              {fireDetections.length === 0 ? (
                <div className="text-center py-8 text-gray-500">
                  <p className="text-lg">✅ No fire detected</p>
                  <p className="text-sm mt-2">This floor is safe</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {fireDetections.map((detection) => (
                    <Card
                      key={detection.id}
                      className={`border-2 ${
                        detection.resolved
                          ? 'border-green-500 bg-green-50'
                          : 'border-red-500 bg-red-50'
                      }`}
                    >
                      <CardContent className="p-4">
                        <div className="flex items-start gap-4">
                          {/* Fire Screenshot */}
                          {detection.screenshot_path && (
                            <div className="flex-shrink-0">
                              <img
                                src={`http://localhost:8000${detection.screenshot_path}`}
                                alt="Fire Detection"
                                className="w-48 h-36 object-cover rounded-lg border-2 border-red-500"
                                onError={(e) => {
                                  e.currentTarget.style.display = 'none';
                                }}
                              />
                            </div>
                          )}
                          
                          {/* Fire Details */}
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                              <span className="text-2xl">🔥</span>
                              <h3 className="font-semibold text-gray-900 capitalize">
                                {detection.fire_type || 'Fire'} Detection
                              </h3>
                              <Badge className={getSeverityColor(detection.severity)}>
                                {detection.severity}
                              </Badge>
                              {detection.resolved ? (
                                <Badge variant="outline" className="bg-green-100 ml-auto">
                                  ✓ Resolved
                                </Badge>
                              ) : (
                                <Badge variant="destructive" className="ml-auto">Active</Badge>
                              )}
                            </div>
                            <div className="grid grid-cols-2 gap-2 text-sm">
                              <div>
                                <span className="text-gray-600">Camera:</span>{' '}
                                <span className="font-medium">#{detection.camera_id}</span>
                              </div>
                              {detection.room && (
                                <div>
                                  <span className="text-gray-600">Location:</span>{' '}
                                  <span className="font-medium">{detection.room}</span>
                                </div>
                              )}
                              <div>
                                <span className="text-gray-600">Confidence:</span>{' '}
                                <span className="font-medium">
                                  {Math.round(detection.confidence * 100)}%
                                </span>
                              </div>
                              <div className="col-span-2">
                                <span className="text-gray-600">Detected:</span>{' '}
                                <span className="font-medium">
                                  {new Date(detection.detected_at).toLocaleString()}
                                </span>
                                <span className="text-gray-500 ml-2">
                                  ({getTimeSince(detection.detected_at)})
                                </span>
                              </div>
                            </div>
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </>
      )}

      {/* All Floors View */}
      {selectedFloor === null && (
        <Card>
          <CardHeader>
            <CardTitle>All Floors Overview</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {floors.map((floor) => (
                <Card
                  key={floor.id}
                  className="cursor-pointer hover:shadow-lg transition-shadow"
                  onClick={() => setSelectedFloor(floor.id)}
                >
                  <CardContent className="p-6">
                    <h3 className="text-xl font-semibold mb-4">{floor.name}</h3>
                    <div className="space-y-2">
                      <div className="flex justify-between">
                        <span className="text-gray-600">People:</span>
                        <span className="font-semibold">-</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Alerts:</span>
                        <span className="font-semibold">-</span>
                      </div>
                    </div>
                    <Button className="w-full mt-4" variant="outline">
                      View Details
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
}
