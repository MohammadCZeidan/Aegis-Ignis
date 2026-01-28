import { BrowserRouter, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { lazy, Suspense } from 'react';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AppProvider } from './contexts/AppContext';
import { NotificationContainer } from './components/NotificationContainer';
import { GlobalLoader } from './components/GlobalLoader';
import { Login } from './views/Login';
import { Landing } from './views/Landing';
import { Layout } from './components/Layout';
// Lazy load views
const Dashboard = lazy(() => import('./views/Dashboard').then(m => ({ default: m.Dashboard })));
const Floors = lazy(() => import('./views/Floors').then(m => ({ default: m.Floors })));
const FloorDetail = lazy(() => import('./views/FloorDetail').then(m => ({ default: m.FloorDetail })));
const Cameras = lazy(() => import('./views/Cameras').then(m => ({ default: m.Cameras })));
const Alerts = lazy(() => import('./views/Alerts').then(m => ({ default: m.Alerts })));
const Settings = lazy(() => import('./views/Settings').then(m => ({ default: m.Settings })));
const Employees = lazy(() => import('./views/Employees').then(m => ({ default: m.Employees })));
const FloorMonitoring = lazy(() => import('./views/FloorMonitoring'));
const LiveCameraView = lazy(() => import('./views/LiveCameraView'));

// Loading component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[400px]">
    <div className="text-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
      <p className="text-slate-600">Loading...</p>
    </div>
  </div>
);

// Protected route wrapper
function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <PageLoader />;
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}

// Create query client with optimized defaults
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 30000, // 30 seconds
      gcTime: 300000, // 5 minutes
    },
  },
});

function AppRoutes() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  return (
    <Routes>
      {/* Public routes */}
      <Route path="/landing" element={<Landing onGetStarted={() => navigate('/login')} />} />
      <Route path="/login" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Login />} />
      
      {/* Protected routes */}
      <Route path="/" element={
        <ProtectedRoute>
          <Layout />
        </ProtectedRoute>
      }>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Suspense fallback={<PageLoader />}><Dashboard /></Suspense>} />
        <Route path="floors" element={<Suspense fallback={<PageLoader />}><Floors /></Suspense>} />
        <Route path="floors/:floorId" element={<Suspense fallback={<PageLoader />}><FloorDetail /></Suspense>} />
        <Route path="cameras" element={<Suspense fallback={<PageLoader />}><Cameras /></Suspense>} />
        <Route path="alerts" element={<Suspense fallback={<PageLoader />}><Alerts /></Suspense>} />
        <Route path="employees" element={<Suspense fallback={<PageLoader />}><Employees /></Suspense>} />
        <Route path="monitoring" element={<Suspense fallback={<PageLoader />}><FloorMonitoring /></Suspense>} />
        <Route path="cameras/live" element={<Suspense fallback={<PageLoader />}><LiveCameraView /></Suspense>} />
        <Route path="settings" element={<Suspense fallback={<PageLoader />}><Settings /></Suspense>} />
      </Route>
      
      {/* Catch all - redirect to landing for unauthenticated, dashboard for authenticated */}
      <Route path="*" element={isAuthenticated ? <Navigate to="/dashboard" replace /> : <Navigate to="/landing" replace />} />
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
        <AuthProvider>
          <AppProvider>
            <AppRoutes />
            <NotificationContainer />
            <GlobalLoader />
            <Toaster 
              position="top-right"
              toastOptions={{
                duration: 3000,
                style: {
                  background: '#363636',
                  color: '#fff',
                },
                success: {
                  duration: 3000,
                  iconTheme: {
                    primary: '#10b981',
                    secondary: '#fff',
                  },
                },
                error: {
                  duration: 4000,
                  iconTheme: {
                    primary: '#ef4444',
                    secondary: '#fff',
                  },
                },
              }}
            />
          </AppProvider>
        </AuthProvider>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
