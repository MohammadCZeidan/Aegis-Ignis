import { Home, Building2, Video, AlertTriangle, Settings, Menu, Users, Activity } from 'lucide-react';
import { Button } from './ui/button';
import { authService } from '../services/auth';

interface SidebarProps {
  currentView: string;
  onViewChange: (view: string) => void;
  collapsed: boolean;
  onToggleCollapse: () => void;
}

export function Sidebar({ currentView, onViewChange, collapsed, onToggleCollapse }: SidebarProps) {
  const isAdmin = authService.isAdmin();
  
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'floors', label: 'Floors', icon: Building2 },
    { id: 'floor-monitoring', label: 'Floor Monitoring', icon: Activity },
    { id: 'cameras', label: 'Cameras', icon: Video },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
    ...(isAdmin ? [{ id: 'employees', label: 'Employees', icon: Users }] : []),
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div 
      className={`bg-[#0F172A] text-white transition-all duration-300 flex flex-col h-full ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="p-4 flex items-center justify-between border-b border-slate-700">
        {!collapsed && <span className="font-bold">SecureWatch</span>}
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleCollapse}
          className="text-white hover:bg-slate-700"
        >
          <Menu className="h-5 w-5" />
        </Button>
      </div>
      
      <nav className="flex-1 p-2">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentView === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onViewChange(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg mb-1 transition-colors ${
                isActive 
                  ? 'bg-blue-600 text-white' 
                  : 'text-slate-300 hover:bg-slate-800 hover:text-white'
              }`}
            >
              <Icon className="h-5 w-5" />
              {!collapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>
    </div>
  );
}
