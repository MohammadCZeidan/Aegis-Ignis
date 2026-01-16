<?php

namespace App\Services;

use App\Models\Employee;
use App\Models\PresenceLog;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\DB;

class PresenceService
{
    public function logPresence(array $data): PresenceLog
    {
        $imagePath = null;
        
        if (isset($data['detection_image'])) {
            $imagePath = $this->storeDetectionImage($data['detection_image'], $data['employee_id']);
        }

        $log = PresenceLog::create([
            'employee_id' => $data['employee_id'],
            'floor_id' => $data['floor_id'] ?? null,
            'room_location' => $data['room_location'] ?? null,
            'camera_id' => $data['camera_id'] ?? null,
            'confidence' => $data['confidence'],
            'detection_image_path' => $imagePath,
            'event_type' => $data['event_type'] ?? 'detected',
            'detected_at' => now(),
        ]);

        $this->updateEmployeeLocation($data['employee_id'], $data);

        return $log;
    }

    public function getPeopleByFloor(int $floorId, ?int $perPage = 15, bool $countOnly = false)
    {
        if ($countOnly) {
            return Employee::where('current_floor_id', $floorId)
                ->where('presence_status', 'in_building')
                ->count();
        }
        
        $employees = Employee::where('current_floor_id', $floorId)
            ->where('presence_status', 'in_building')
            ->with('floor')
            ->get();
            
        $formatted = $employees->map(function ($employee) {
            return $this->formatEmployeeForList($employee);
        });
        
        return [
            'data' => $formatted,
            'total' => $formatted->count()
        ];
    }

    public function getAllPeopleInBuilding(?int $perPage = 20, array $filters = [])
    {
        $query = Employee::where('presence_status', 'in_building')
            ->with(['floor', 'department']);

        if (isset($filters['floor_id'])) {
            $query->where('current_floor_id', $filters['floor_id']);
        }

        if (isset($filters['room'])) {
            $query->where('current_room', 'like', '%' . $filters['room'] . '%');
        }

        if (isset($filters['search'])) {
            $query->where(function($q) use ($filters) {
                $q->where('name', 'like', '%' . $filters['search'] . '%')
                  ->orWhere('employee_number', 'like', '%' . $filters['search'] . '%')
                  ->orWhere('email', 'like', '%' . $filters['search'] . '%');
            });
        }

        $employees = $query->orderBy('last_seen_at', 'desc')->get();
        
        $formatted = $employees->map(function ($employee) {
            return [
                'id' => $employee->id,
                'name' => $employee->name,
                'employee_number' => $employee->employee_number,
                'email' => $employee->email,
                'phone' => $employee->phone,
                'department' => $employee->department?->name,
                'floor' => $employee->floor?->name,
                'floor_id' => $employee->current_floor_id,
                'current_room' => $employee->current_room,
                'last_seen_at' => $employee->last_seen_at?->diffForHumans(),
                'last_seen_timestamp' => $employee->last_seen_at,
                'face_photo_url' => $employee->face_photo_path 
                    ? Storage::url($employee->face_photo_path) 
                    : null,
                'photo_url' => $employee->photo_path 
                    ? Storage::url($employee->photo_path) 
                    : null,
                'presence_status' => $employee->presence_status,
            ];
        });
        
        return [
            'data' => $formatted,
            'total' => $formatted->count()
        ];
    }

    public function getEmployeeDetails(int $id): array
    {
        $employee = Employee::with(['floor', 'department'])->findOrFail($id);
        $recentLogs = $this->getRecentPresenceLogs($id);

        return [
            'employee' => $this->formatEmployeeDetails($employee),
            'recent_activity' => $recentLogs
        ];
    }

    public function getOccupancyStats(): array
    {
        $byFloor = Employee::where('presence_status', 'in_building')
            ->select('current_floor_id', DB::raw('count(*) as count'))
            ->groupBy('current_floor_id')
            ->with('floor')
            ->get()
            ->map(function ($item) {
                return [
                    'floor_id' => $item->current_floor_id,
                    'floor_name' => $item->floor?->name ?? 'Unknown',
                    'count' => $item->count
                ];
            });

        return [
            'total_in_building' => Employee::where('presence_status', 'in_building')->count(),
            'by_floor' => $byFloor,
            'total_registered_faces' => Employee::whereNotNull('face_embedding')->count(),
        ];
    }

    public function logEntry(string $employeeName, array $data): bool
    {
        $employee = Employee::where('name', $employeeName)->first();
        
        if (!$employee) {
            return false;
        }

        PresenceLog::create([
            'employee_id' => $employee->id,
            'floor_id' => $data['floor_id'] ?? null,
            'room_location' => $data['room'] ?? null,
            'camera_id' => $data['camera_id'] ?? null,
            'event_type' => 'entry',
            'detected_at' => $data['timestamp'] ?? now(),
        ]);

        $employee->update([
            'current_floor_id' => $data['floor_id'] ?? $employee->current_floor_id,
            'current_room' => $data['room'] ?? $employee->current_room,
            'last_seen_at' => now(),
            'last_camera_id' => $data['camera_id'] ?? $employee->last_camera_id,
            'presence_status' => 'in_building'
        ]);

        return true;
    }

    public function logExit(string $employeeName, array $data): bool
    {
        $employee = Employee::where('name', $employeeName)->first();
        
        if (!$employee) {
            return false;
        }

        PresenceLog::create([
            'employee_id' => $employee->id,
            'event_type' => 'exit',
            'detected_at' => $data['timestamp'] ?? now(),
        ]);

        $employee->update([
            'presence_status' => 'left_building',
            'current_room' => null,
        ]);

        return true;
    }

    public function getCurrentPresence(): array
    {
        $people = Employee::where('presence_status', 'in_building')
            ->with(['floor'])
            ->get()
            ->map(function ($employee) {
                return [
                    'name' => $employee->name,
                    'floor' => $employee->floor?->name ?? 'Unknown',
                    'room' => $employee->current_room,
                    'last_seen' => $employee->last_seen_at?->diffForHumans(),
                ];
            });

        return [
            'people' => $people,
            'count' => $people->count()
        ];
    }

    public function formatEmployeeForList($employee): array
    {
        return [
            'id' => $employee->id,
            'name' => $employee->name,
            'employee_number' => $employee->employee_number,
            'email' => $employee->email,
            'phone' => $employee->phone ?? null,
            'department' => $employee->department ?? null,
            'current_room' => $employee->current_room,
            'last_seen_at' => $employee->last_seen_at,
            'face_photo_url' => $employee->face_photo_path 
                ? Storage::url($employee->face_photo_path) 
                : null,
            'photo_url' => $employee->photo_path 
                ? Storage::url($employee->photo_path) 
                : null,
            'presence_status' => $employee->presence_status,
            'face_registered' => !is_null($employee->face_embedding),
        ];
    }

    private function storeDetectionImage(string $imageData, int $employeeId): string
    {
        $decodedImage = base64_decode($imageData);
        $filename = 'detections/' . time() . '_' . $employeeId . '.jpg';
        Storage::disk('public')->put($filename, $decodedImage);
        
        return $filename;
    }

    private function updateEmployeeLocation(int $employeeId, array $data): void
    {
        $employee = Employee::find($employeeId);
        
        $employee->update([
            'current_floor_id' => $data['floor_id'] ?? $employee->current_floor_id,
            'current_room' => $data['room_location'] ?? $employee->current_room,
            'last_seen_at' => now(),
            'last_camera_id' => $data['camera_id'] ?? $employee->last_camera_id,
            'presence_status' => 'in_building'
        ]);
    }

    private function getRecentPresenceLogs(int $employeeId)
    {
        return PresenceLog::where('employee_id', $employeeId)
            ->with('floor')
            ->orderBy('detected_at', 'desc')
            ->take(10)
            ->get()
            ->map(function ($log) {
                return [
                    'id' => $log->id,
                    'floor' => $log->floor?->name,
                    'room_location' => $log->room_location,
                    'camera_id' => $log->camera_id,
                    'confidence' => $log->confidence,
                    'event_type' => $log->event_type,
                    'detected_at' => $log->detected_at->diffForHumans(),
                    'detected_timestamp' => $log->detected_at,
                    'image_url' => $log->detection_image_path 
                        ? Storage::url($log->detection_image_path) 
                        : null,
                ];
            });
    }

    private function formatEmployeeDetails($employee): array
    {
        return [
            'id' => $employee->id,
            'name' => $employee->name,
            'employee_number' => $employee->employee_number,
            'email' => $employee->email,
            'phone' => $employee->phone,
            'department' => $employee->department?->name,
            'floor' => $employee->floor?->name,
            'floor_id' => $employee->current_floor_id,
            'current_room' => $employee->current_room,
            'last_seen_at' => $employee->last_seen_at?->diffForHumans(),
            'last_seen_timestamp' => $employee->last_seen_at,
            'face_photo_url' => $employee->face_photo_path 
                ? Storage::url($employee->face_photo_path) 
                : null,
            'photo_url' => $employee->photo_path 
                ? Storage::url($employee->photo_path) 
                : null,
            'presence_status' => $employee->presence_status,
            'face_registered_at' => $employee->face_registered_at,
        ];
    }
}
