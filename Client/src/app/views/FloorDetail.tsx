import { useParams, useNavigate } from 'react-router-dom';
import { ArrowLeft, Users, MapPin, Activity } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { CameraCard } from '../components/CameraCard';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { useFloors, useCameras, useFloorOccupancy } from '../hooks/useData';
import { useMemo } from 'react';

export function FloorDetail() {
  const { floorId } = useParams<{ floorId: string }>();
  const navigate = useNavigate();
  
  const { data: floors = [], isLoading: floorsLoading } = useFloors();
  const { data: allCameras = [], isLoading: camerasLoading } = useCameras();
  const { data: occupancyData, isLoading: occupancyLoading } = useFloorOccupancy(parseInt(floorId || '0'));

  const floor = useMemo(() => 
    floors.find(f => f.id.toString() === floorId),
    [floors, floorId]
  );

  const cameras = useMemo(() => 
    allCameras.filter(c => c.floor_id?.toString() === floorId),
    [allCameras, floorId]
  );

  const isLoading = floorsLoading || camerasLoading || occupancyLoading;

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading floor details...</p>
        </div>
      </div>
    );
  }

  if (!floor) {
    return (
      <div className="p-6">
        <p className="text-slate-500">Floor not found</p>
      </div>
    );
  }

  const currentOccupancy = occupancyData?.person_count || 0;
  const maxOccupancy = floor.max_occupancy || 50;
  const occupancyPercentage = (currentOccupancy / maxOccupancy) * 100;
  const people = occupancyData?.people_list || [];

  const statusConfig = {
    normal: { color: 'bg-green-500', label: 'Normal' },
    warning: { color: 'bg-orange-500', label: 'Warning' },
    critical: { color: 'bg-red-500', label: 'Critical' }
  };

  const getStatus = () => {
    if (occupancyPercentage > 90) return 'critical';
    if (occupancyPercentage > 70) return 'warning';
    return 'normal';
  };

  const status = getStatus();
  const config = statusConfig[status];

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="sm" onClick={() => navigate('/floors')} className="h-10 w-10 p-0">
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex-1">
            <h1 className="text-2xl font-bold text-slate-900">{floor.name || `Floor ${floor.floor_number}`}</h1>
            <p className="text-slate-600">Floor {floor.floor_number} Monitoring</p>
          </div>
          <Badge className={`${config.color} text-white`}>
            {config.label}
          </Badge>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-blue-100 rounded-lg">
              <Users className="h-6 w-6 text-blue-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Current Occupancy</p>
              <p className="text-2xl font-bold">{currentOccupancy}/{maxOccupancy}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-purple-100 rounded-lg">
              <Activity className="h-6 w-6 text-purple-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Active Cameras</p>
              <p className="text-2xl font-bold">{cameras.filter(c => c.is_active).length}/{cameras.length}</p>
            </div>
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-center gap-3">
            <div className="p-3 bg-green-100 rounded-lg">
              <MapPin className="h-6 w-6 text-green-600" />
            </div>
            <div>
              <p className="text-sm text-slate-600">Capacity</p>
              <p className="text-2xl font-bold">{Math.round(occupancyPercentage)}%</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Occupancy Bar */}
      <Card className="p-4">
        <h3 className="font-semibold mb-3">Occupancy Level</h3>
        <div className="w-full bg-slate-200 rounded-full h-4">
          <div 
            className={`h-4 rounded-full transition-all ${config.color}`}
            style={{ width: `${Math.min(occupancyPercentage, 100)}%` }}
          />
        </div>
      </Card>

      {/* People Present */}
      {people.length > 0 && (
        <Card className="p-6">
          <h3 className="font-semibold mb-4">People Present ({people.length})</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {people.map((person, index) => (
              <div key={index} className="flex items-center gap-3 p-3 bg-slate-50 rounded-lg">
                <Avatar>
                  <AvatarFallback>
                    {person.name?.split(' ').map(n => n[0]).join('') || '?'}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <p className="font-medium text-sm">{person.name || 'Unknown'}</p>
                  <p className="text-xs text-slate-500">
                    Confidence: {Math.round((person.confidence || 0) * 100)}%
                  </p>
                </div>
              </div>
            ))}
          </div>
        </Card>
      )}

      {/* Cameras */}
      <div>
        <h3 className="font-semibold mb-4">Cameras ({cameras.length})</h3>
        {cameras.length === 0 ? (
          <Card className="p-8 text-center">
            <p className="text-slate-500">No cameras on this floor</p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
            {cameras.map((camera) => (
              <CameraCard
                key={camera.id}
                camera={{
                  id: camera.id.toString(),
                  name: camera.name,
                  status: camera.is_active ? 'online' : 'offline',
                  floorId: camera.floor_id?.toString() || '',
                  location: camera.room || '',
                  streamUrl: camera.stream_url,
                  rtspUrl: camera.rtsp_url,
                }}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
