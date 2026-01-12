import { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';

interface AppContextType {
  sidebarCollapsed: boolean;
  toggleSidebar: () => void;
  setSidebarCollapsed: (collapsed: boolean) => void;
  buildingName: string;
  setBuildingName: (name: string) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [buildingName, setBuildingNameState] = useState('TechCorp HQ');

  // Load building name from API on mount
  useEffect(() => {
    const loadBuildingName = async () => {
      try {
        const response = await fetch('http://localhost:8000/api/v1/building/config');
        const data = await response.json();
        if (data.success && data.data?.name) {
          setBuildingNameState(data.data.name);
        }
      } catch (error) {
        console.error('Failed to load building name:', error);
      }
    };
    loadBuildingName();
  }, []);

  const toggleSidebar = useCallback(() => {
    setSidebarCollapsed(prev => !prev);
  }, []);

  const setBuildingName = useCallback((name: string) => {
    setBuildingNameState(name);
  }, []);

  return (
    <AppContext.Provider value={{ 
      sidebarCollapsed, 
      toggleSidebar, 
      setSidebarCollapsed,
      buildingName,
      setBuildingName
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useApp() {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useApp must be used within AppProvider');
  }
  return context;
}
