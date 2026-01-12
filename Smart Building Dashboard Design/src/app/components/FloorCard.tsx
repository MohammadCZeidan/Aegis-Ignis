import { memo } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Floor } from '../data/mockData';
import { Building2, Users, ArrowRight } from 'lucide-react';

interface FloorCardProps {
  floor: Floor;
  onViewDetails: (floorId: string) => void;
}

const FloorCardComponent = ({ floor, onViewDetails }: FloorCardProps) => {
  const statusConfig = {
    normal: { color: 'bg-green-500', label: 'Normal', variant: 'outline' as const },
    warning: { color: 'bg-orange-500', label: 'Warning', variant: 'outline' as const },
    critical: { color: 'bg-red-500', label: 'Critical', variant: 'destructive' as const }
  };

  const config = statusConfig[floor.status];
  const occupancyPercentage = (floor.occupancy / floor.maxOccupancy) * 100;

  return (
    <Card className="p-5 lg:p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="p-3 lg:p-4 bg-blue-50 rounded-lg">
            <Building2 className="h-6 w-6 lg:h-7 lg:w-7 text-blue-600" />
          </div>
          <div>
            <h3 className="text-lg lg:text-xl text-slate-900">{floor.name}</h3>
            <p className="text-sm text-slate-500">Floor {floor.number}</p>
          </div>
        </div>
        <div className={`w-4 h-4 rounded-full ${config.color}`} />
      </div>

      <div className="mb-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2 text-slate-600">
            <Users className="h-5 w-5" />
            <span className="text-sm lg:text-base">Occupancy</span>
          </div>
          <span className="text-xl lg:text-2xl text-slate-900">
            {floor.occupancy} / {floor.maxOccupancy}
          </span>
        </div>
        <div className="w-full bg-slate-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full transition-all ${
              occupancyPercentage > 80 ? 'bg-red-500' : 
              occupancyPercentage > 60 ? 'bg-orange-500' : 
              'bg-green-500'
            }`}
            style={{ width: `${occupancyPercentage}%` }}
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <Badge variant={config.variant} className="text-sm py-1 px-3">{config.label}</Badge>
        <Button 
          variant="ghost" 
          size="sm"
          onClick={() => onViewDetails(floor.id)}
          className="text-blue-600 hover:text-blue-700 h-10"
        >
          View Details
          <ArrowRight className="h-4 w-4 ml-1" />
        </Button>
      </div>
    </Card>
  );
};

// Memoize to prevent unnecessary re-renders
export const FloorCard = memo(FloorCardComponent, (prevProps, nextProps) => {
  return (
    prevProps.floor.id === nextProps.floor.id &&
    prevProps.floor.occupancy === nextProps.floor.occupancy &&
    prevProps.floor.status === nextProps.floor.status
  );
});