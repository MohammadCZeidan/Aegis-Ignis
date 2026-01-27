import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { Login } from './components/Login';
import { FaceRegistration } from './components/FaceRegistration';
import { Landing } from './components/Landing';
import { authService } from './services/auth';

// Loading component
function LoadingScreen() {
  return (
    <div className="h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-slate-100">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-slate-600">Loading...</p>
      </div>
    </div>
  );
}

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      if (authService.isAuthenticated()) {
        const user = await authService.getCurrentUser();
        setIsAuthenticated(!!user);
      }
      setIsLoading(false);
    };
    checkAuth();
  }, []);

  if (isLoading) {
    return <LoadingScreen />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

function AppRoutes() {
  const navigate = useNavigate();
  
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/landing" element={<Landing onGetStarted={() => navigate('/login')} />} />
      <Route path="/login" element={<Login onLoginSuccess={() => window.location.href = '/employees'} />} />
      
      {/* Protected routes */}
      <Route
        path="/employees"
        element={
          <ProtectedRoute>
            <FaceRegistration onLogout={() => {
              authService.logout();
              window.location.href = '/login';
            }} />
          </ProtectedRoute>
        }
      />
      
      {/* Redirect root to landing */}
      <Route path="/" element={<Navigate to="/landing" replace />} />
      
      {/* Catch all - redirect to landing */}
      <Route path="*" element={<Navigate to="/landing" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  );
}

export default App;

