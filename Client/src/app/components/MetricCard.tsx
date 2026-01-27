import { Card } from './ui/card';
import { LucideIcon, TrendingUp, TrendingDown } from 'lucide-react';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: 'up' | 'down';
  trendValue?: string;
  status?: 'normal' | 'warning' | 'critical';
  subtitle?: string;
}

export function MetricCard({ title, value, icon: Icon, trend, trendValue, status = 'normal', subtitle }: MetricCardProps) {
  const statusColors = {
    normal: 'text-green-600 bg-green-50',
    warning: 'text-orange-600 bg-orange-50',
    critical: 'text-red-600 bg-red-50'
  };

  return (
    <Card className="p-5 lg:p-6">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm lg:text-base text-slate-600 mb-2">{title}</p>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl lg:text-3xl text-slate-900">{value}</span>
            {trend && trendValue && (
              <span className={`flex items-center gap-1 text-xs lg:text-sm ${
                trend === 'up' ? 'text-green-600' : 'text-red-600'
              }`}>
                {trend === 'up' ? <TrendingUp className="h-3 w-3 lg:h-4 lg:w-4" /> : <TrendingDown className="h-3 w-3 lg:h-4 lg:w-4" />}
                {trendValue}
              </span>
            )}
          </div>
          {subtitle && <p className="text-xs lg:text-sm text-slate-500 mt-2">{subtitle}</p>}
        </div>
        <div className={`p-3 lg:p-4 rounded-lg ${statusColors[status]}`}>
          <Icon className="h-6 w-6 lg:h-7 lg:w-7" />
        </div>
      </div>
    </Card>
  );
}