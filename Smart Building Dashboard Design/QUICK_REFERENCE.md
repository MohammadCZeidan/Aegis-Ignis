# 🎯 Quick Reference - Optimized Dashboard

## Common Tasks

### Adding a New Page
```tsx
// 1. Create view in src/app/views/MyView.tsx
export function MyView() {
  return <div>My View</div>;
}

// 2. Add route in src/app/App.tsx
<Route path="myview" element={<Suspense fallback={<PageLoader />}><MyView /></Suspense>} />

// 3. Add to Sidebar navigation
{ id: 'myview', label: 'My View', icon: MyIcon }
```

### Fetching Data
```tsx
import { useFloors, useCameras, useEmployees } from '../hooks/useData';

function MyComponent() {
  const { data, isLoading, error, refetch } = useFloors();
  
  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage error={error} />;
  
  return <div>{/* Use data */}</div>;
}
```

### Navigation
```tsx
import { useNavigate, useParams } from 'react-router-dom';

function MyComponent() {
  const navigate = useNavigate();
  const { id } = useParams();
  
  // Navigate to different pages
  navigate('/floors');
  navigate(`/floors/${id}`);
  navigate(-1); // Go back
}
```

### Using Auth
```tsx
import { useAuth } from '../contexts/AuthContext';

function MyComponent() {
  const { user, isAuthenticated, login, logout, isAdmin } = useAuth();
  
  if (!isAuthenticated) return <Login />;
  if (isAdmin()) return <AdminPanel />;
}
```

### Creating New Data Hook
```tsx
// In src/app/hooks/useData.ts
export function useMyData() {
  return useQuery({
    queryKey: ['mydata'],
    queryFn: () => dataService.getMyData(),
    staleTime: 30000,
    refetchInterval: 60000,
  });
}

// Mutation example
export function useCreateMyData() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data) => dataService.createMyData(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['mydata'] });
    },
  });
}
```

## File Locations

```
Key Files:
├── src/app/App.tsx                   - Main app & routing
├── src/app/components/Layout.tsx     - Layout wrapper
├── src/app/contexts/AuthContext.tsx  - Authentication
├── src/app/contexts/AppContext.tsx   - Global state
├── src/app/hooks/useData.ts          - Data fetching
├── src/app/hooks/useCommon.ts        - Utilities
└── vite.config.ts                    - Build config
```

## Performance Tips

1. **Use React.memo for expensive components**
   ```tsx
   const MyComponent = memo(function MyComponent({ data }) {
     // Component logic
   });
   ```

2. **Memoize computed values**
   ```tsx
   const filteredData = useMemo(() => 
     data.filter(item => item.active),
     [data]
   );
   ```

3. **Stable callbacks**
   ```tsx
   const handleClick = useCallback(() => {
     // Handler logic
   }, [dependencies]);
   ```

4. **Lazy load heavy components**
   ```tsx
   const HeavyComponent = lazy(() => import('./HeavyComponent'));
   ```

## React Query Patterns

### Basic Query
```tsx
const { data, isLoading, error } = useQuery({
  queryKey: ['key'],
  queryFn: fetchFunction,
});
```

### Query with Params
```tsx
const { data } = useQuery({
  queryKey: ['floors', floorId],
  queryFn: () => fetchFloor(floorId),
  enabled: !!floorId, // Only run if floorId exists
});
```

### Mutation
```tsx
const mutation = useMutation({
  mutationFn: createFloor,
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['floors'] });
  },
});

// Use it
mutation.mutate(newFloorData);
```

### Manual Refetch
```tsx
const { refetch } = useFloors();
<Button onClick={() => refetch()}>Refresh</Button>
```

## Routing Patterns

### Simple Navigation
```tsx
<Button onClick={() => navigate('/floors')}>
  View Floors
</Button>
```

### Navigation with Data
```tsx
<Button onClick={() => navigate(`/floors/${floor.id}`)}>
  View Details
</Button>
```

### Get Current Route
```tsx
const location = useLocation();
const isActive = location.pathname === '/floors';
```

### Protected Routes
```tsx
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" />;
  return children;
}
```

## Common Imports

```tsx
// Routing
import { useNavigate, useParams, useLocation } from 'react-router-dom';

// Data
import { useFloors, useCameras, useEmployees } from '../hooks/useData';
import { useQueryClient } from '@tanstack/react-query';

// Auth & State
import { useAuth } from '../contexts/AuthContext';
import { useApp } from '../contexts/AppContext';

// React
import { useState, useEffect, useMemo, useCallback, memo } from 'react';

// UI Components
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
```

## Debugging

### Check Cache
```tsx
import { useQueryClient } from '@tanstack/react-query';

const queryClient = useQueryClient();
console.log(queryClient.getQueryData(['floors']));
```

### Force Refetch
```tsx
queryClient.invalidateQueries({ queryKey: ['floors'] });
```

### Clear All Cache
```tsx
queryClient.clear();
```

## Build & Deploy

```bash
# Development
npm run dev

# Production Build
npm run build

# Preview Production
npm run preview

# Check Bundle Size
npm run build -- --report
```

## Environment Variables

Create `.env` file:
```env
VITE_API_URL=http://localhost:8000/api/v1
```

Use in code:
```tsx
const apiUrl = import.meta.env.VITE_API_URL;
```

---

**Pro Tip:** Keep components small and focused. Extract reusable logic into custom hooks!
