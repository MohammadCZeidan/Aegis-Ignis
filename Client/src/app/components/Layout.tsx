import { useState } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { Sidebar } from './Sidebar';
import { Header } from './Header';
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';
import { Home, Building2, Video, AlertTriangle, Settings as SettingsIcon, Users, Activity } from 'lucide-react';

export function Layout() {
  const navigate = useNavigate();
  const location = useLocation();
  const { logout, isAdmin } = useAuth();
  const { sidebarCollapsed, toggleSidebar } = useApp();

  const getCurrentView = () => {
    const path = location.pathname.split('/')[1] || 'dashboard';
    if (path === '') return 'dashboard';
    if (path === 'monitoring') return 'floor-monitoring';
    return path;
  };
  const handleViewChange = (view: string) => {
    const routes: Record<string, string> = {
      dashboard: '/',
      floors: '/floors',
      'floor-monitoring': '/monitoring',
      cameras: '/cameras',
      alerts: '/alerts',
      employees: '/employees',
      settings: '/settings',
    };
    navigate(routes[view] || '/');
  };

  const mobileNavItems = [
    { id: 'dashboard', label: 'Dashboard', icon: Home },
    { id: 'floors', label: 'Floors', icon: Building2 },
    { id: 'floor-monitoring', label: 'Monitor', icon: Activity },
    { id: 'cameras', label: 'Cameras', icon: Video },
    { id: 'alerts', label: 'Alerts', icon: AlertTriangle },
    ...(isAdmin() ? [{ id: 'employees', label: 'Employees', icon: Users }] : []),
    { id: 'settings', label: 'Settings', icon: SettingsIcon },
  ];

  const currentView = getCurrentView();

  return (
    <div className="h-screen flex bg-slate-50">
      {/* Desktop Sidebar */}
      <div className="hidden lg:flex h-full">
        <Sidebar 
          currentView={currentView}
          onViewChange={handleViewChange}
          collapsed={sidebarCollapsed}
          onToggleCollapse={toggleSidebar}
        />
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden h-full">
        {/* Desktop Header */}
        <div className="hidden lg:block w-full">
          <Header onLogout={logout} />
        </div>
        
        {/* Page Content */}
        <main className="flex-1 overflow-y-auto pb-20 lg:pb-0">
          <Outlet />
        </main>

        {/* Mobile Bottom Navigation */}
        <div className="lg:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-slate-200 z-50">
          <div className="grid grid-cols-5 gap-1">
            {mobileNavItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentView === item.id;
              
              return (
                <button
                  key={item.id}
                  onClick={() => handleViewChange(item.id)}
                  className={`flex flex-col items-center justify-center py-3 px-2 transition-colors ${
                    isActive 
                      ? 'text-blue-600' 
                      : 'text-slate-600'
                  }`}
                >
                  <Icon className={`h-6 w-6 mb-1 ${isActive ? 'stroke-[2.5]' : ''}`} />
                  <span className="text-xs">{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
