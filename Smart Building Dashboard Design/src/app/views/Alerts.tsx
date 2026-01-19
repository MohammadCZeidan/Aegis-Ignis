import { useState, useEffect } from 'react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Card } from '../components/ui/card';
import { AlertTriangle, Flame, CheckCircle, Building2, Camera, Clock } from 'lucide-react';
import { dataService } from '../services/dataService';
import { toast } from 'react-hot-toast';

const LARAVEL_API_URL = 'http://35.180.117.85/api/v1';
const LARAVEL_BASE_URL = 'http://35.180.117.85';

interface Alert {
  id: number;
  event_type: string;
  severity: string;
  floor_id: number;
  camera_id: string;
  camera_name: string;
  room: string;
  confidence: number;
  fire_type: string;
  screenshot_path: string;
  image?: string; // Base64 encoded image data
  detected_at: string;
  status: string;
  resolved?: boolean;
  resolved_at?: string;
  created_at: string;
}

interface Floor {
  id: number;
  name: string;
}

export function Alerts() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [floors, setFloors] = useState<Floor[]>([]);
  const [selectedFloor, setSelectedFloor] = useState<string>('all');
  const [viewMode, setViewMode] = useState<'active' | 'all'>('active');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
    
    // Refresh alerts every 10 seconds
    const interval = setInterval(loadData, 10000);
    
    return () => clearInterval(interval);
  }, []);

  const loadData = async () => {
    try {
      const [alertsData, floorsData] = await Promise.all([
        fetch(`${LARAVEL_API_URL}/alerts`).then(r => r.json()),
        dataService.getFloors()
      ]);
      
      console.log('Alerts API Response:', alertsData); // Debug log
      
      // Handle different response formats
      let alertsList = [];
      if (Array.isArray(alertsData)) {
        alertsList = alertsData;
      } else if (alertsData.alerts && Array.isArray(alertsData.alerts)) {
        alertsList = alertsData.alerts;
      } else if (alertsData.success !== false) {
        alertsList = Object.values(alertsData).filter(item => typeof item === 'object' && item.id);
      }
      
      console.log('Processed alerts:', alertsList.length); // Debug log
      setAlerts(alertsList);
      setFloors(floorsData);
    } catch (error) {
      console.error('Failed to load alerts:', error);
    } finally {
      setLoading(false);
    }
  };

  const acknowledgeAlert = async (alertId: number) => {
    try {
      const response = await fetch(`${LARAVEL_API_URL}/alerts/${alertId}/acknowledge`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      
      if (!response.ok) throw new Error('Failed to acknowledge');
      
      toast.success('Alert acknowledged and resolved');
      loadData();
    } catch (error) {
      console.error('Failed to acknowledge alert:', error);
      toast.error('Failed to acknowledge alert');
    }
  };

  // Filter by view mode (active or all)
  const viewFilteredAlerts = viewMode === 'active' 
    ? alerts.filter(a => a.status === 'active' && !a.resolved)  // Exclude resolved alerts from active view
    : alerts;

  // Filter by floor
  const filteredAlerts = selectedFloor === 'all' 
    ? viewFilteredAlerts 
    : viewFilteredAlerts.filter(alert => alert.floor_id?.toString() === selectedFloor);

  const activeAlerts = alerts.filter(a => a.status === 'active' && !a.resolved);  // Only truly active alerts
  const alertsByFloor = filteredAlerts.reduce((acc, alert) => {
    const floorId = alert.floor_id || 0;
    if (!acc[floorId]) acc[floorId] = [];
    acc[floorId].push(alert);
    return acc;
  }, {} as Record<number, Alert[]>);

  if (loading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading alerts...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl lg:text-2xl font-bold text-slate-900">Fire Detection Alerts</h1>
          <p className="text-sm lg:text-base text-slate-500">Real-time fire detection with camera screenshots</p>
        </div>
        <div className="flex items-center gap-2">
          <Badge variant="outline" className={activeAlerts.length > 0 ? "bg-red-50 text-red-600 border-red-200 py-2 px-4" : "bg-green-50 text-green-600 border-green-200 py-2 px-4"}>
            {activeAlerts.length} Active Alert{activeAlerts.length !== 1 ? 's' : ''}
          </Badge>
        </div>
      </div>

      {/* View Mode Toggle */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="flex gap-2">
          <Button
            variant={viewMode === 'active' ? 'default' : 'outline'}
            onClick={() => setViewMode('active')}
            className="flex-1 sm:flex-initial"
          >
            <Flame className="h-4 w-4 mr-2" />
            Active Alerts ({activeAlerts.length})
          </Button>
          <Button
            variant={viewMode === 'all' ? 'default' : 'outline'}
            onClick={() => setViewMode('all')}
            className="flex-1 sm:flex-initial"
          >
            <Clock className="h-4 w-4 mr-2" />
            All History ({alerts.length})
          </Button>
        </div>
      </div>

      {/* Floor Filter */}
      <div className="flex flex-col gap-3 p-4 lg:p-6 bg-white rounded-lg border border-slate-200">
        <div className="flex items-center gap-2">
          <Building2 className="h-5 w-5 text-slate-600" />
          <span className="text-slate-600">Filter by Floor</span>
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Button
            size="sm"
            variant={selectedFloor === 'all' ? 'default' : 'outline'}
            onClick={() => setSelectedFloor('all')}
            className="h-10"
          >
            All Floors
          </Button>
          {floors.map(floor => {
            const floorAlerts = viewFilteredAlerts.filter(a => a.floor_id === floor.id);
            return (
              <Button
                key={floor.id}
                size="sm"
                variant={selectedFloor === floor.id.toString() ? 'default' : 'outline'}
                onClick={() => setSelectedFloor(floor.id.toString())}
                className="h-10"
              >
                {floor.name}
                {floorAlerts.length > 0 && (
                  <Badge variant="destructive" className="ml-2 h-5 min-w-5 px-1">
                    {floorAlerts.length}
                  </Badge>
                )}
              </Button>
            );
          })}
        </div>
      </div>

      <div className="space-y-6">
        {Object.keys(alertsByFloor).length > 0 ? (
          Object.entries(alertsByFloor).map(([floorId, floorAlerts]) => {
            const floor = floors.find(f => f.id === Number(floorId));
            return (
              <div key={floorId} className="space-y-4">
                <div className="flex items-center gap-3">
                  <Building2 className="h-5 w-5 text-slate-600" />
                  <h2 className="text-lg font-semibold text-slate-900">
                    {floor?.name || `Floor ${floorId}`}
                  </h2>
                  <Badge variant="outline">
                    {floorAlerts.length} alert{floorAlerts.length !== 1 ? 's' : ''}
                  </Badge>
                </div>
                
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                  {floorAlerts.map((alert) => (
                    <Card key={alert.id} className={`overflow-hidden ${alert.status === 'active' ? 'border-red-300 bg-red-50' : 'border-slate-200'}`}>
                      {/* Screenshot */}
                      {(alert.image || alert.screenshot_path) && (
                        <div className="relative bg-slate-900 aspect-video">
                          <img 
                            src={alert.image ? `data:image/jpeg;base64,${alert.image}` : `${LARAVEL_BASE_URL}${alert.screenshot_path}`}
                            alt="Fire detection"
                            className="w-full h-full object-cover"
                            onLoad={() => console.log(`Image loaded for alert ${alert.id}`)}
                            onError={(e) => {
                              console.error(`Image failed to load for alert ${alert.id}:`, e);
                              console.log(`Image source:`, alert.image ? 'base64 data' : `${LARAVEL_BASE_URL}${alert.screenshot_path}`);
                              const target = e.target as HTMLImageElement;
                              target.style.display = 'none';
                            }}
                          />
                          <div className="absolute top-3 left-3 bg-red-600 text-white px-3 py-1 rounded text-sm font-semibold">
                            🔥 FIRE DETECTED
                          </div>
                        </div>
                      )}
                      
                      {/* Alert Details */}
                      <div className="p-4">
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-2">
                            <Flame className={`h-5 w-5 ${alert.status === 'active' ? 'text-red-600' : 'text-orange-500'}`} />
                            <div>
                              <h3 className="font-semibold text-slate-900">{alert.camera_name}</h3>
                              <p className="text-sm text-slate-600">{alert.room}</p>
                            </div>
                          </div>
                          <Badge variant={alert.status === 'active' ? 'destructive' : 'secondary'}>
                            {alert.status}
                          </Badge>
                        </div>
                        
                        <div className="space-y-2 text-sm">
                          <div className="flex items-center gap-2 text-slate-600">
                            <Camera className="h-4 w-4" />
                            <span>Camera: {alert.camera_id}</span>
                          </div>
                          
                          <div className="flex items-center gap-2 text-slate-600">
                            <Clock className="h-4 w-4" />
                            <span>{new Date(alert.detected_at || alert.created_at).toLocaleString()}</span>
                          </div>
                          
                          <div className="flex items-center justify-between pt-2">
                            <div className="flex items-center gap-2">
                              <span className="text-slate-700 font-medium">Confidence:</span>
                              <Badge variant={alert.confidence > 0.7 ? 'destructive' : 'secondary'}>
                                {Math.round(alert.confidence * 100)}%
                              </Badge>
                            </div>
                            
                            <Badge variant="outline" className="capitalize">
                              {alert.severity}
                            </Badge>
                          </div>
                        </div>
                        
                        {alert.status === 'active' && (
                          <Button 
                            variant="destructive" 
                            size="sm" 
                            className="w-full mt-4"
                            onClick={() => acknowledgeAlert(alert.id)}
                          >
                            <AlertTriangle className="h-4 w-4 mr-2" />
                            Acknowledge Alert
                          </Button>
                        )}
                      </div>
                    </Card>
                  ))}
                </div>
              </div>
            );
          })
        ) : (
          <Card className="p-12 text-center">
            <CheckCircle className="h-16 w-16 text-green-500 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-slate-900 mb-2">
              {viewMode === 'active' ? 'All Clear' : 'No Alerts Found'}
            </h3>
            <p className="text-slate-600">
              {viewMode === 'active' 
                ? 'No active fire alerts at this time' 
                : 'No fire alerts in history for selected filters'}
            </p>
            <p className="text-sm text-slate-500 mt-2">
              {viewMode === 'active' && 'System is actively monitoring all cameras for fire and smoke'}
            </p>
          </Card>
        )}
      </div>

      <Card className="p-6 bg-blue-50 border-blue-200">
        <div className="flex items-start gap-3">
          <AlertTriangle className="h-5 w-5 text-blue-600 mt-0.5" />
          <div>
            <h3 className="font-semibold text-blue-900 mb-1">Detection Information</h3>
            <p className="text-sm text-blue-800">
              Fire detection system monitors all cameras in real-time. Alerts include screenshots captured at the moment of detection.
              The system tracks person presence and will notify when someone leaves (not seen for 5 minutes).
            </p>
          </div>
        </div>
      </Card>
    </div>
  );
}
