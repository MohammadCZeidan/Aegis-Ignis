import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { dataService } from '../services/dataService';

// Query keys for consistent caching
export const queryKeys = {
  floors: ['floors'] as const,
  floor: (id: number) => ['floor', id] as const,
  cameras: ['cameras'] as const,
  camera: (id: number) => ['camera', id] as const,
  employees: ['employees'] as const,
  employee: (id: number) => ['employee', id] as const,
  occupancy: ['occupancy'] as const,
  floorOccupancy: (floorId: number) => ['occupancy', floorId] as const,
  alerts: ['alerts'] as const,
};

// Floors
export function useFloors() {
  return useQuery({
    queryKey: queryKeys.floors,
    queryFn: () => dataService.getFloors(),
    staleTime: 30000, // 30 seconds
    refetchInterval: 60000, // Refetch every minute
  });
}

// Floor detail is fetched from floors list

export function useCreateFloor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => dataService.createFloor(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.floors });
    },
  });
}

export function useUpdateFloor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: number; data: any }) => dataService.updateFloor(id, data),
    onSuccess: (_, variables) => {
      queryClient.invalidateQueries({ queryKey: queryKeys.floors });
      queryClient.invalidateQueries({ queryKey: queryKeys.floor(variables.id) });
    },
  });
}

export function useDeleteFloor() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => dataService.deleteFloor(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.floors });
    },
  });
}

// Cameras
export function useCameras() {
  return useQuery({
    queryKey: queryKeys.cameras,
    queryFn: () => dataService.getCameras(),
    staleTime: 30000,
    refetchInterval: 60000,
  });
}

// Employees
export function useEmployees() {
  return useQuery({
    queryKey: queryKeys.employees,
    queryFn: () => dataService.getEmployees(),
    staleTime: 60000, // 1 minute
  });
}

// Employee mutations will be added when backend supports them



export function useDeleteEmployee() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => dataService.deleteEmployee(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.employees });
    },
  });
}

// Occupancy
export function useOccupancy() {
  return useQuery({
    queryKey: queryKeys.occupancy,
    queryFn: () => dataService.getAllOccupancy(),
    staleTime: 10000, // 10 seconds
    refetchInterval: 15000, // Refetch every 15 seconds
  });
}

export function useFloorOccupancy(floorId: number) {
  return useQuery({
    queryKey: queryKeys.floorOccupancy(floorId),
    queryFn: () => dataService.getFloorOccupancy(floorId),
    enabled: !!floorId,
    staleTime: 10000,
    refetchInterval: 15000,
  });
}

// Alerts
export function useAlerts() {
  return useQuery({
    queryKey: queryKeys.alerts,
    queryFn: () => dataService.getAlerts(),
    staleTime: 5000, // 5 seconds - alerts need to be fresh
    refetchInterval: 10000, // Refetch every 10 seconds for real-time updates
  });
}

export function useActiveAlerts() {
  return useQuery({
    queryKey: ['alerts', 'active'],
    queryFn: () => dataService.getActiveAlerts(),
    staleTime: 3000,
    refetchInterval: 5000, // More frequent for active alerts
  });
}

export function useAcknowledgeAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => dataService.acknowledgeAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.alerts });
      queryClient.invalidateQueries({ queryKey: ['alerts', 'active'] });
    },
  });
}

export function useResolveAlert() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => dataService.resolveAlert(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.alerts });
      queryClient.invalidateQueries({ queryKey: ['alerts', 'active'] });
    },
  });
}
