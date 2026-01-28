import { useState, useEffect } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { API_CONFIG, buildBackendUrl } from '../../config/api';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';


import { 
  Building2, 
  Video, 
  Users, 
  Bell, 
  Phone, 
  Activity,
  Save,
  MapPin
} from 'lucide-react';
import { dataService } from '../services/dataService';
import { notificationService } from '../services/notificationService';
import { loadingService } from '../services/loadingService';
import { useApp } from '../contexts/AppContext';

interface CameraFloorAssignment {
  cameraId: string;
  cameraName: string;
  floorId: string;
  location: string;
}

export function Settings() {
  const { buildingName: globalBuildingName, setBuildingName: setGlobalBuildingName } = useApp();
  const [cameraAssignments, setCameraAssignments] = useState<CameraFloorAssignment[]>([]);
  const [floors, setFloors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [buildingName, setBuildingName] = useState(globalBuildingName);
  const [totalFloors, setTotalFloors] = useState(3);

  useEffect(() => {
    loadData();
    loadBuildingConfig();
  }, []);

  const loadBuildingConfig = async () => {
    try {
      const token = localStorage.getItem('aegis_auth_token');
      const response = await fetch(`${API_CONFIG.BACKEND_API}/building/config`, {
        headers: token ? { 'Authorization': `Bearer ${token}` } : {}
      });
      if (response.ok) {
        const data = await response.json();
        if (data.data) {
          setBuildingName(data.data.name || 'Aegis Building');
          setTotalFloors(data.data.total_floors || 3);
        }
      }
    } catch (error) {
      console.log('Could not load building config, using defaults');
    }
  };

  const loadData = async () => {
    setLoading(true);
    try {
      const [camerasData, floorsData] = await Promise.all([
        dataService.getCameras(),
        dataService.getFloors(),
      ]);
      const assignments = camerasData.map(cam => ({
        cameraId: cam.id.toString(),
        cameraName: cam.name,
        floorId: cam.floor_id.toString(),
        location: cam.room || ''
      }));
      
      console.log('Loaded cameras:', assignments);
      console.log('Loaded floors:', floorsData);
      
      setCameraAssignments(assignments);
      setFloors(floorsData);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleFloorChange = (cameraId: string, newFloorId: string) => {
    setCameraAssignments(prev =>
      prev.map(assignment =>
        assignment.cameraId === cameraId
          ? { ...assignment, floorId: newFloorId }
          : assignment
      )
    );
  };

  const handleLocationChange = (cameraId: string, newLocation: string) => {
    setCameraAssignments(prev =>
      prev.map(assignment =>
        assignment.cameraId === cameraId
          ? { ...assignment, location: newLocation }
          : assignment
      )
    );
  };

  const handleSaveAssignments = async () => {
    try {
      await loadingService.withLoading(async () => {
        // 1. Update Laravel backend (database)
        console.log('Updating Laravel database...');
        const updatePromises = cameraAssignments.map(assignment =>
          dataService.updateCamera(parseInt(assignment.cameraId), {
            floor_id: parseInt(assignment.floorId),
            room: assignment.location
          })
        );
        
        await Promise.all(updatePromises);
        console.log('✓ Laravel database updated');
        
        // 2. Update streaming server
        let streamingServerUpdated = false;
        try {
          console.log('Updating camera streaming server...');
          console.log('Sending assignments:', cameraAssignments);
          const streamResponse = await fetch(`${API_CONFIG.CAMERA_SERVICE}/api/cameras/update-config`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ assignments: cameraAssignments })
          });
          
          console.log('Stream server response status:', streamResponse.status);
          if (streamResponse.ok) {
            const result = await streamResponse.json();
            console.log('✓ Streaming server updated:', result);
            streamingServerUpdated = true;
          } else {
            console.error('Stream server error:', await streamResponse.text());
          }
        } catch (streamError) {
          console.error('[WARNING] Streaming server error:', streamError);
        }
        
        // 3. Update floor monitoring service
        let floorMonitoringUpdated = false;
        try {
          console.log('Updating floor monitoring service...');
          console.log('Sending assignments:', cameraAssignments);
          const floorResponse = await fetch(`${API_CONFIG.FLOOR_SERVICE}/api/cameras/update-floor-assignments`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ assignments: cameraAssignments })
          });
          
          console.log('Floor monitoring response status:', floorResponse.status);
          if (floorResponse.ok) {
            const result = await floorResponse.json();
            console.log('✓ Floor monitoring updated:', result);
            floorMonitoringUpdated = true;
          } else {
            console.error('Floor monitoring error:', await floorResponse.text());
          }
        } catch (floorError) {
          console.error('[WARNING] Floor monitoring error:', floorError);
        }
        
        // Show success notification
        if (streamingServerUpdated && floorMonitoringUpdated) {
          notificationService.success('Camera assignments saved successfully!', {
            description: 'Database, streaming server, and floor monitoring updated. All services now use new floor assignments.',
            duration: 4000,
          });
        } else if (streamingServerUpdated || floorMonitoringUpdated) {
          notificationService.warning('Camera assignments partially saved', {
            description: `Database updated. ${streamingServerUpdated ? 'Streaming ✓' : 'Streaming ✗'} ${floorMonitoringUpdated ? 'Monitoring ✓' : 'Monitoring ✗'}`,
            duration: 5000,
          });
        } else {
          notificationService.warning('Camera assignments saved to database', {
            description: 'Streaming server not running. Start it to apply changes.',
            duration: 5000,
          });
        }
        
        // Reload to reflect changes
        await loadData();
      }, 'Saving camera assignments...');
      
    } catch (error) {
      console.error('[ERROR] Failed to save assignments:', error);
      notificationService.error('Failed to save camera assignments', {
        description: error instanceof Error ? error.message : 'Please try again',
        duration: 5000,
      });
    }
  };
  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div>
        <h1 className="text-xl lg:text-2xl text-slate-900">Settings</h1>
        <p className="text-sm lg:text-base text-slate-500">Configure system preferences and camera assignments</p>
      </div>

      {/* Camera to Floor Assignments */}
      <Card className="p-5 lg:p-6">
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-blue-50 rounded-lg">
              <MapPin className="h-5 w-5 text-blue-600" />
            </div>
            <div>
              <h3 className="text-lg text-slate-900">Camera Floor Assignments</h3>
              <p className="text-sm text-slate-500">Assign cameras to specific floors and locations</p>
            </div>
          </div>
          <Button onClick={handleSaveAssignments} className="gap-2">
            <Save className="h-4 w-4" />
            Save All
          </Button>
        </div>

        <div className="space-y-4 max-h-96 overflow-y-auto">
          {cameraAssignments.map((assignment) => (
            <div key={assignment.cameraId} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <Label className="text-xs text-slate-600">Camera</Label>
                  <div className="flex items-center gap-2 mt-1">
                    <Video className="h-4 w-4 text-slate-400" />
                    <span className="font-medium text-slate-900">{assignment.cameraName}</span>
                  </div>
                </div>
                
                <div>
                  <Label htmlFor={`floor-${assignment.cameraId}`} className="text-xs text-slate-600">
                    Floor Assignment
                  </Label>
                  <Select
                    value={assignment.floorId}
                    onValueChange={(value) => handleFloorChange(assignment.cameraId, value)}
                  >
                    <SelectTrigger id={`floor-${assignment.cameraId}`} className="mt-1">
                      <SelectValue placeholder="Select floor" />
                    </SelectTrigger>
                    <SelectContent>
                      {floors.map((floor) => (
                        <SelectItem key={floor.id} value={floor.id.toString()}>
                          {floor.name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <Label htmlFor={`location-${assignment.cameraId}`} className="text-xs text-slate-600">
                    Specific Location
                  </Label>
                  <Input
                    id={`location-${assignment.cameraId}`}
                    value={assignment.location}
                    onChange={(e) => handleLocationChange(assignment.cameraId, e.target.value)}
                    placeholder="e.g., Main Entrance"
                    className="mt-1"
                  />
                </div>
              </div>
            </div>
          ))}
        </div>

        {cameraAssignments.length === 0 && (
          <div className="text-center py-8 text-slate-500">
            <Video className="h-12 w-12 mx-auto mb-2 text-slate-300" />
            <p>No cameras found. Start the camera streaming server to see cameras.</p>
          </div>
        )}
      </Card>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
        {/* Building Configuration */}
        <Card className="p-5 lg:p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-blue-50 rounded-lg">
              <Building2 className="h-5 w-5 text-blue-600" />
            </div>
            <h3 className="text-lg font-semibold text-slate-900">Building Configuration</h3>
          </div>
          <div className="space-y-4">
            <div>
              <Label htmlFor="building-name">Building Name</Label>
              <Input 
                id="building-name" 
                value={buildingName}
                onChange={(e) => setBuildingName(e.target.value)}
                className="mt-2 h-11" 
              />
            </div>
            <div>
              <Label htmlFor="total-floors">Total Floors</Label>
              <Input 
                id="total-floors" 
                type="number" 
                value={totalFloors}
                onChange={(e) => setTotalFloors(parseInt(e.target.value) || 1)}
                min="1"
                max="100"
                className="mt-2 h-11" 
              />
            </div>
            <Button 
              onClick={async () => {
                try {
                  const token = localStorage.getItem('aegis_auth_token');
                  const response = await fetch(buildBackendUrl('/building/config'), {
                    method: 'PUT',
                    headers: { 
                      'Content-Type': 'application/json',
                      ...(token ? { 'Authorization': `Bearer ${token}` } : {})
                    },
                    body: JSON.stringify({ 
                      name: buildingName, 
                      total_floors: totalFloors 
                    })
                  });
                  if (response.ok) {
                    // Update global building name immediately
                    setGlobalBuildingName(buildingName);
                    notificationService.success('Building configuration saved successfully!');
                  } else {
                    notificationService.error('Failed to save configuration');
                  }
                } catch (error) {
                  notificationService.error('Error saving configuration');
                }
              }}
              className="w-full"
            >
              <Save className="h-4 w-4 mr-2" />
              Save Building Config
            </Button>
          </div>
        </Card>

        {/* Camera Settings */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-purple-50 rounded-lg">
              <Video className="h-5 w-5 text-purple-600" />
            </div>
            <h3 className="text-slate-900">Camera Settings</h3>
          </div>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <Label>Auto-record on detection</Label>
                <p className="text-sm text-slate-500">Record video when fire/smoke detected</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Show bounding boxes</Label>
                <p className="text-sm text-slate-500">Display detection overlays</p>
              </div>
              <Switch defaultChecked />
            </div>
            <div>
              <Label htmlFor="retention">Recording Retention (days)</Label>
              <Input id="retention" type="number" defaultValue="30" />
            </div>
          </div>
        </Card>

        {/* Alert Thresholds */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-orange-50 rounded-lg">
              <Bell className="h-5 w-5 text-orange-600" />
            </div>
            <h3 className="text-slate-900">Alert Thresholds</h3>
          </div>
          <div className="space-y-4">
            <div>
              <Label htmlFor="fire-confidence">Fire Detection Confidence (%)</Label>
              <Input id="fire-confidence" type="number" defaultValue="85" />
            </div>
            <div>
              <Label htmlFor="smoke-confidence">Smoke Detection Confidence (%)</Label>
              <Input id="smoke-confidence" type="number" defaultValue="75" />
            </div>
            <div>
              <Label htmlFor="occupancy-warning">Occupancy Warning Level (%)</Label>
              <Input id="occupancy-warning" type="number" defaultValue="80" />
            </div>
            <Button>Update Thresholds</Button>
          </div>
        </Card>

        {/* Emergency Contacts */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-red-50 rounded-lg">
              <Phone className="h-5 w-5 text-red-600" />
            </div>
            <h3 className="text-slate-900">Emergency Contacts</h3>
          </div>
          <div className="space-y-4">
            <div>
              <Label htmlFor="fire-dept">Fire Department</Label>
              <Input id="fire-dept" type="tel" defaultValue="911" />
            </div>
            <div>
              <Label htmlFor="security">Security Office</Label>
              <Input id="security" type="tel" defaultValue="+1 (555) 123-4567" />
            </div>
            <div>
              <Label htmlFor="building-manager">Building Manager</Label>
              <Input id="building-manager" type="tel" defaultValue="+1 (555) 987-6543" />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Auto-call emergency services</Label>
                <p className="text-sm text-slate-500">On critical fire detection</p>
              </div>
              <Switch defaultChecked />
            </div>
            <Button>Save Contacts</Button>
          </div>
        </Card>

        {/* Employee Management */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-green-50 rounded-lg">
              <Users className="h-5 w-5 text-green-600" />
            </div>
            <h3 className="text-slate-900">Employee Database</h3>
          </div>
          <div className="space-y-4">
            <p className="text-sm text-slate-500">
              Manage employee records and upload photos for facial recognition.
            </p>
            <div className="flex gap-2">
              <Button variant="outline">Import CSV</Button>
              <Button variant="outline">Add Employee</Button>
            </div>
            <div className="pt-4 border-t">
              <p className="text-sm text-slate-600">Total Employees: 247</p>
              <p className="text-sm text-slate-600">With Photos: 186</p>
            </div>
          </div>
        </Card>

        {/* System Health */}
        <Card className="p-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="p-2 bg-cyan-50 rounded-lg">
              <Activity className="h-5 w-5 text-cyan-600" />
            </div>
            <h3 className="text-slate-900">System Health</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm text-slate-600">AI Detection Model</span>
              <span className="text-sm text-green-600 font-medium">Active</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm text-slate-600">Database Connection</span>
              <span className="text-sm text-green-600 font-medium">Connected</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm text-slate-600">Video Stream Server</span>
              <span className="text-sm text-green-600 font-medium">Online</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm text-slate-600">Storage Usage</span>
              <span className="text-sm text-slate-600 font-medium">1.2 TB / 5 TB</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}