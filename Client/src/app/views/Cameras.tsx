import { useState, useMemo, memo } from 'react';
import { CameraCard } from '../components/CameraCard';
import { Video, RefreshCw } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { useCameras, useFloors } from '../hooks/useData';
import { useQueryClient } from '@tanstack/react-query';
import { queryKeys } from '../hooks/useData';

const STREAMING_SERVER = 'http://localhost:5000';

export function Cameras() {
  const queryClient = useQueryClient();
  const [selectedFloor, setSelectedFloor] = useState<string>('all');
  const { data: cameras = [], isLoading: camerasLoading, refetch } = useCameras();
  const { data: floors = [], isLoading: floorsLoading } = useFloors();

  const filteredCameras = useMemo(() => 
    selectedFloor === 'all' 
      ? cameras 
      : cameras.filter(cam => cam.floor_id?.toString() === selectedFloor),
    [cameras, selectedFloor]
  );

  const stats = useMemo(() => ({
    online: cameras.filter(c => c.is_active).length,
    total: cameras.length,
    monitoring: cameras.filter(c => c.is_active).length,
  }), [cameras]);

  const handleRefresh = () => {
    queryClient.invalidateQueries({ queryKey: queryKeys.cameras });
    refetch();
  };

  const isLoading = camerasLoading || floorsLoading;

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading cameras...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 mb-2">Camera Management</h1>
          <p className="text-slate-600">Monitor all surveillance cameras in real-time</p>
        </div>
        <Button onClick={handleRefresh} variant="outline">
          <RefreshCw className="h-4 w-4 mr-2" />
          Refresh
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-4">
        <Card className="p-4 bg-green-50 border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-green-700 font-medium">Online Cameras/Total Cameras</p>
              <p className="text-2xl font-bold text-green-700">{stats.online}/{stats.total}</p>
            </div>
            <Video className="h-8 w-8 text-green-600" />
          </div>
        </Card>
      </div>

      {/* Floor Filter */}
      <div className="flex flex-wrap gap-2">
        <Button
          variant={selectedFloor === 'all' ? 'default' : 'outline'}
          size="sm"
          onClick={() => setSelectedFloor('all')}
        >
          All Floors ({cameras.length})
        </Button>
        {floors.map((floor) => {
          const floorCamCount = cameras.filter(c => c.floor_id === floor.id).length;
          return (
            <Button
              key={floor.id}
              variant={selectedFloor === floor.id.toString() ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedFloor(floor.id.toString())}
            >
              {floor.name || `Floor ${floor.floor_number}`} ({floorCamCount})
            </Button>
          );
        })}
      </div>

      {/* Camera Grid */}
      {filteredCameras.length === 0 ? (
        <Card className="p-12 text-center">
          <Video className="h-12 w-12 text-slate-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-slate-900 mb-2">No Cameras Found</h3>
          <p className="text-slate-600">
            {selectedFloor === 'all' 
              ? 'No cameras have been configured yet.'
              : 'No cameras found on this floor.'}
          </p>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredCameras.map((camera) => (
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
  );
}
