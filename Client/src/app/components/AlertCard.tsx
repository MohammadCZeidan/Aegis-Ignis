import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Alert, getFloorById, getCameraById } from '../data/mockData';
import { Flame, CloudFog, ShieldAlert, Clock } from 'lucide-react';

interface AlertCardProps {
  alert: Alert;
  onAcknowledge?: (alertId: string) => void;
  compact?: boolean;
}
export function AlertCard({ alert, onAcknowledge, compact = false }: AlertCardProps) {
  const floor = getFloorById(alert.floorId);
  const camera = getCameraById(alert.cameraId);

  const typeConfig = {
    fire: { icon: Flame, color: 'text-red-600', bgColor: 'bg-red-50', label: 'Fire' },
    smoke: { icon: CloudFog, color: 'text-orange-600', bgColor: 'bg-orange-50', label: 'Smoke' },
    security: { icon: ShieldAlert, color: 'text-blue-600', bgColor: 'bg-blue-50', label: 'Security' }
  };

  const severityConfig = {
    low: { variant: 'outline' as const, label: 'Low' },
    medium: { variant: 'secondary' as const, label: 'Medium' },
    high: { variant: 'default' as const, label: 'High' },
    critical: { variant: 'destructive' as const, label: 'Critical' }
  };

  const statusConfig = {
    active: { color: 'text-red-600', label: 'Active' },
    acknowledged: { color: 'text-orange-600', label: 'Acknowledged' },
    resolved: { color: 'text-green-600', label: 'Resolved' }
  };

  const config = typeConfig[alert.type];
  const Icon = config.icon;
  
  const formatTime = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / 60000);
    
    if (diffInMinutes < 1) return 'Just now';
    if (diffInMinutes < 60) return `${diffInMinutes} min ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} hr ago`;
    return date.toLocaleDateString();
  };

  if (compact) {
    return (
      <div className="flex items-center gap-3 p-4 hover:bg-slate-50 rounded-lg transition-colors">
        <div className={`p-3 rounded-lg ${config.bgColor}`}>
          <Icon className={`h-6 w-6 ${config.color}`} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm lg:text-base text-slate-900 truncate">{alert.message}</p>
          <p className="text-xs lg:text-sm text-slate-500">{floor?.name} • {formatTime(alert.timestamp)}</p>
        </div>
        <Badge variant={severityConfig[alert.severity].variant} className="text-xs lg:text-sm">
          {severityConfig[alert.severity].label}
        </Badge>
      </div>
    );
  }

  return (
    <Card className="p-5 lg:p-6">
      <div className="flex items-start gap-4">
        <div className={`p-3 lg:p-4 rounded-lg ${config.bgColor} flex-shrink-0`}>
          <Icon className={`h-6 w-6 lg:h-7 lg:w-7 ${config.color}`} />
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-2">
            <div>
              <h4 className="text-slate-900">{alert.message}</h4>
              <div className="flex items-center gap-2 mt-1 text-sm text-slate-500">
                <span>{floor?.name}</span>
                <span>•</span>
                <span>{camera?.name}</span>
              </div>
            </div>
            <Badge variant={severityConfig[alert.severity].variant}>
              {severityConfig[alert.severity].label}
            </Badge>
          </div>
          
          <div className="flex items-center gap-4 text-sm">
            <div className="flex items-center gap-1 text-slate-600">
              <Clock className="h-4 w-4" />
              {formatTime(alert.timestamp)}
            </div>
            <span className={`font-medium ${statusConfig[alert.status].color}`}>
              {statusConfig[alert.status].label}
            </span>
            {alert.emergencyCallStatus && (
              <Badge variant="outline" className="text-xs">
                Emergency: {alert.emergencyCallStatus}
              </Badge>
            )}
          </div>
          
          {alert.status === 'active' && onAcknowledge && (
            <div className="mt-3">
              <Button 
                size="sm" 
                variant="outline"
                onClick={() => onAcknowledge(alert.id)}
              >
                Acknowledge
              </Button>
            </div>
          )}
        </div>
      </div>
    </Card>
  );
}