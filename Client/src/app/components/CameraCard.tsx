import { memo } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Camera } from '../data/mockData';
import { Video, Maximize2, Circle, Flame, User, AlertTriangle } from 'lucide-react';
import { FireDetection, FaceDetection } from '../services/detectionService';

const STREAMING_SERVER = 'http://localhost:5000';

interface CameraCardProps {
  camera: Camera & { streamUrl?: string };
  onFullscreen?: (cameraId: string) => void;
  fireDetections?: FireDetection[];
  faceDetections?: FaceDetection[];
}
function CameraCardComponent({ camera, onFullscreen, fireDetections = [], faceDetections = [] }: CameraCardProps) {
  const isOnline = camera.status === 'online';
  const streamUrl = camera.streamUrl || `${STREAMING_SERVER}/video_feed/${camera.id}`;
  
  const hasFireAlert = fireDetections.length > 0;
  const detectedPeople = faceDetections.filter(d => d.cameraId === camera.id);

  return (
    <Card className={`overflow-hidden ${hasFireAlert ? 'ring-2 ring-red-500 animate-pulse' : ''}`}>
      <div className="relative bg-slate-900 aspect-video">
        {/* Live camera feed or offline placeholder */}
        {isOnline ? (
          <div className="relative w-full h-full">
            {/* Live MJPEG stream */}
            <img
              src={streamUrl}
              alt={camera.name}
              className="w-full h-full object-cover"
              style={{ display: 'block' }}
            />
            
            {/* Live indicator */}
            <div className="absolute top-3 left-3 flex items-center gap-2 bg-red-600 text-white px-2 py-1 lg:px-3 lg:py-1.5 rounded text-xs lg:text-sm z-10">
              <Circle className="h-2 w-2 fill-white animate-pulse" />
              LIVE
            </div>
            
            {/* Fire Alert Overlay */}
            {hasFireAlert && (
              <div className="absolute top-3 right-3 flex items-center gap-2 bg-red-600 text-white px-3 py-2 rounded-lg shadow-lg z-10 animate-pulse">
                <Flame className="h-5 w-5" />
                <div className="text-left">
                  <p className="text-xs font-bold">FIRE DETECTED!</p>
                  <p className="text-xs">{Math.round(fireDetections[0].confidence * 100)}% confident</p>
                </div>
              </div>
            )}
            
            {/* People Detected Overlay */}
            {detectedPeople.length > 0 && (
              <div className="absolute bottom-3 left-3 bg-blue-900/90 text-white px-3 py-2 rounded-lg text-xs z-10 max-w-[200px]">
                <div className="flex items-center gap-2 mb-1">
                  <User className="h-4 w-4" />
                  <span className="font-semibold">{detectedPeople.length} Person{detectedPeople.length > 1 ? 's' : ''}</span>
                </div>
                {detectedPeople.slice(0, 3).map((detection, idx) => (
                  <div key={idx} className="text-xs truncate">
                    • {detection.personName}
                  </div>
                ))}
                {detectedPeople.length > 3 && (
                  <div className="text-xs opacity-75">+{detectedPeople.length - 3} more</div>
                )}
              </div>
            )}
            
            {/* Fullscreen button */}
            {onFullscreen && (
              <Button
                size="sm"
                variant="ghost"
                className="absolute bottom-3 right-3 text-white hover:bg-white/20 h-10 w-10 p-0 z-10"
                onClick={() => onFullscreen(camera.id)}
              >
                <Maximize2 className="h-5 w-5" />
              </Button>
            )}
          </div>
        ) : (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-2 text-slate-600">
            <Video className="h-12 w-12 lg:h-16 lg:w-16" />
            <span className="text-sm lg:text-base">Camera Offline</span>
          </div>
        )}
      </div>
      
      <div className="p-4 lg:p-5">
        <div className="flex items-center justify-between mb-2">
          <h4 className="text-base lg:text-lg text-slate-900">{camera.name}</h4>
          <div className="flex items-center gap-2">
            {hasFireAlert && (
              <Badge variant="destructive" className="text-xs animate-pulse">
                <AlertTriangle className="h-3 w-3 mr-1" />
                FIRE
              </Badge>
            )}
            <Badge variant={isOnline ? 'default' : 'secondary'} className={`${isOnline ? 'bg-green-600' : ''} text-xs lg:text-sm py-1`}>
              {camera.status}
            </Badge>
          </div>
        </div>
        <p className="text-sm lg:text-base text-slate-500">{camera.location}</p>
        
        {/* Detection Summary */}
        {(detectedPeople.length > 0 || hasFireAlert) && (
          <div className="mt-3 pt-3 border-t border-slate-200 flex items-center gap-3 text-xs">
            {detectedPeople.length > 0 && (
              <div className="flex items-center gap-1 text-blue-600">
                <User className="h-3 w-3" />
                <span>{detectedPeople.length} detected</span>
              </div>
            )}
            {hasFireAlert && (
              <div className="flex items-center gap-1 text-red-600 font-semibold">
                <Flame className="h-3 w-3" />
                <span>Fire alert active</span>
              </div>
            )}
          </div>
        )}
      </div>
    </Card>
  );
}

// Memoize component to prevent unnecessary re-renders
export const CameraCard = memo(CameraCardComponent, (prevProps, nextProps) => {
  return (
    prevProps.camera.id === nextProps.camera.id &&
    prevProps.camera.status === nextProps.camera.status &&
    prevProps.fireDetections?.length === nextProps.fireDetections?.length &&
    prevProps.faceDetections?.length === nextProps.faceDetections?.length
  );
});