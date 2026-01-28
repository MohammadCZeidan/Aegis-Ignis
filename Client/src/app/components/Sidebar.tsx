import { Home, Building2, Video, AlertTriangle, Settings, Menu, Users, Activity } from 'lucide-react';
import { Button } from './ui/button';
import { authService } from '../services/auth';
import logo from '../../assets/aegis-logo.png';

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
      className={`bg-gradient-to-b from-slate-900 via-slate-900 to-slate-950 text-white transition-all duration-300 flex flex-col h-full border-r border-white/10 backdrop-blur-xl ${
        collapsed ? 'w-16' : 'w-64'
      }`}
    >
      <div className="p-4 flex items-center justify-between border-b border-white/10">
        {!collapsed ? (
          <div className="flex items-center gap-2">
            <img src={logo} alt="Aegis Ignis" className="h-10 w-10 drop-shadow-lg" />
            <div>
              <span className="font-bold text-lg bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">Aegis Ignis</span>
              <p className="text-xs text-slate-400">Security System</p>
            </div>
          </div>
        ) : (
          <img src={logo} alt="Aegis Ignis" className="h-8 w-8 mx-auto drop-shadow-lg" />
        )}
        <Button
          variant="ghost"
          size="sm"
          onClick={onToggleCollapse}
          className="text-white hover:bg-white/10"
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
              className={`w-full flex items-center gap-3 px-3 py-3 rounded-lg mb-1 transition-all duration-200 ${
                isActive 
                  ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white shadow-lg shadow-blue-500/30' 
                  : 'text-slate-300 hover:bg-white/5 hover:text-white hover:scale-105'
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
