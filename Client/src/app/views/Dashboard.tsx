import { useMemo, memo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Users, AlertTriangle, Video, Shield, Building2 } from 'lucide-react';
import { Card } from '../components/ui/card';
import { useFloors, useCameras, useEmployees, useAlerts } from '../hooks/useData';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: React.ElementType;
  status: 'normal' | 'warning' | 'critical';
  subtitle?: string;
  onClick?: () => void;
}
const MetricCard = memo(function MetricCard({ title, value, icon: Icon, status, subtitle, onClick }: MetricCardProps) {
  const statusColors = {
    normal: 'bg-green-50 border-green-200 text-green-700',
    warning: 'bg-amber-50 border-amber-200 text-amber-700',
    critical: 'bg-red-50 border-red-200 text-red-700'
  };

  return (
    <Card 
      className={`p-4 border ${statusColors[status]} ${onClick ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between mb-2">
        <Icon className="h-5 w-5" />
        <span className="text-2xl font-bold">{value}</span>
      </div>
      <h3 className="font-medium text-sm">{title}</h3>
      {subtitle && <p className="text-xs opacity-75 mt-1">{subtitle}</p>}
    </Card>
  );
});

export function Dashboard() {
  const navigate = useNavigate();
  const { data: floors = [], isLoading: floorsLoading } = useFloors();
  const { data: cameras = [], isLoading: camerasLoading } = useCameras();
  const { data: employees = [], isLoading: employeesLoading } = useEmployees();
  const { data: alerts = [], isLoading: alertsLoading } = useAlerts();

  const metrics = useMemo(() => {
    const onlineCameras = cameras.filter(c => c.is_active).length;
    const activeAlerts = alerts.filter(a => a.status === 'active').length;
    const criticalAlerts = alerts.filter(a => a.severity === 'critical' && a.status === 'active').length;

    return {
      onlineCameras,
      totalCameras: cameras.length,
      activeAlerts,
      criticalAlerts,
      totalEmployees: employees.length,
      totalFloors: floors.length,
    };
  }, [cameras, alerts, employees, floors]);

  const isLoading = floorsLoading || camerasLoading || employeesLoading || alertsLoading;

  if (isLoading) {
    return (
      <div className="p-6 flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-slate-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 lg:p-6 space-y-6">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">Dashboard Overview</h1>
        <p className="text-slate-600">Real-time monitoring of your smart building</p>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Active Alerts"
          value={metrics.activeAlerts}
          icon={AlertTriangle}
          status={metrics.criticalAlerts > 0 ? 'critical' : metrics.activeAlerts > 0 ? 'warning' : 'normal'}
          subtitle={metrics.criticalAlerts > 0 ? `${metrics.criticalAlerts} critical` : 'All systems normal'}
          onClick={() => navigate('/alerts')}
        />
        
        <MetricCard
          title="Building Floors"
          value={metrics.totalFloors}
          icon={Building2}
          status="normal"
          subtitle="Total floors monitored"
          onClick={() => navigate('/floors')}
        />
        
        <MetricCard
          title="Registered Employees"
          value={metrics.totalEmployees}
          icon={Users}
          status="normal"
          subtitle="Total registered"
          onClick={() => navigate('/employees')}
        />
        
        <MetricCard
          title="Active Cameras"
          value={`${metrics.onlineCameras}/${metrics.totalCameras}`}
          icon={Video}
          status={metrics.onlineCameras < metrics.totalCameras ? 'warning' : 'normal'}
          subtitle="Monitoring in progress"
          onClick={() => navigate('/cameras')}
        />
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-6">
        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Recent Alerts</h2>
          {alerts.length === 0 ? (
            <p className="text-slate-500 text-sm">No recent alerts</p>
          ) : (
            <div className="space-y-3">
              {alerts.slice(0, 5).map((alert) => (
                <div key={alert.id} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                  <div className="flex items-center gap-3">
                    <AlertTriangle className={`h-5 w-5 ${
                      alert.severity === 'critical' ? 'text-red-600' : 
                      alert.severity === 'warning' ? 'text-amber-600' : 'text-slate-600'
                    }`} />
                    <div>
                      <p className="font-medium text-sm">{alert.event_type}</p>
                      <p className="text-xs text-slate-500">{new Date(alert.created_at).toLocaleString()}</p>
                    </div>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded ${
                    alert.status === 'active' ? 'bg-red-100 text-red-700' : 'bg-green-100 text-green-700'
                  }`}>
                    {alert.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">System Status</h2>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Camera Network</span>
              <span className="text-sm font-medium text-green-600">Operational</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Face Recognition</span>
              <span className="text-sm font-medium text-green-600">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Fire Detection</span>
              <span className="text-sm font-medium text-green-600">Active</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-sm text-slate-600">Database</span>
              <span className="text-sm font-medium text-green-600">Connected</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
}
