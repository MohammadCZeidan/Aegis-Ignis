<?php

namespace App\Services;

use App\Models\Alert;
use App\Models\EmergencyAlert;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;

class AlertService
{
    public function getAllAlerts(array $filters = []): array
    {
        try {
            $query = Alert::with(['floor', 'fireEvent']);

            $this->applyFilters($query, $filters);

            $alerts = $query->orderBy('created_at', 'desc')
                ->get()
                ->map(function ($alert) {
                    return $this->transformAlertData($alert);
                });

            return [
                'success' => true,
                'alerts' => $alerts
            ];
        } catch (\Exception $e) {
            Log::error('Failed to fetch alerts', ['error' => $e->getMessage()]);
            return [
                'success' => true,
                'alerts' => []
            ];
        }
    }

    public function getAlertById(int $id): array
    {
        try {
            $alert = Alert::with(['floor', 'fireEvent'])->findOrFail($id);
            return [
                'success' => true,
                'alert' => $alert
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'error' => 'Alert not found'
            ];
        }
    }

    public function getAlertsByFloor(int $floorId): Collection
    {
        return Alert::where('floor_id', $floorId)
            ->orderBy('created_at', 'desc')
            ->get()
            ->map(function ($alert) {
                return $this->transformAlertData($alert);
            });
    }

    public function acknowledgeAlert(int $id, ?string $acknowledgedBy = null): array
    {
        try {
            $alert = Alert::findOrFail($id);
            $alert->update([
                'status' => 'resolved',
                'resolved' => true,
                'resolved_at' => now()
            ]);

            return [
                'success' => true,
                'message' => 'Alert acknowledged and resolved',
                'alert' => $alert
            ];
        } catch (\Exception $e) {
            return [
                'success' => false,
                'error' => 'Failed to acknowledge alert: ' . $e->getMessage()
            ];
        }
    }

    public function createFireAlert(array $data): array
    {
        try {
            $alertData = $this->prepareFireAlertData($data);
            $alert = Alert::create($alertData);

            Log::info('Fire alert created', [
                'alert_id' => $alert->id,
                'camera' => $data['camera_name'] ?? 'Unknown',
                'floor' => $data['floor_id'] ?? 'Unknown'
            ]);

            return [
                'success' => true,
                'alert' => $alert
            ];
        } catch (\Exception $e) {
            Log::error('Failed to create fire alert', [
                'error' => $e->getMessage(),
                'request' => $data
            ]);

            return [
                'success' => false,
                'error' => 'Failed to create alert'
            ];
        }
    }

    private function applyFilters($query, array $filters): void
    {
        if (isset($filters['status'])) {
            $query->where('status', $filters['status']);
        }

        if (isset($filters['event_type'])) {
            $query->where('event_type', $filters['event_type']);
        }

        if (isset($filters['floor_id'])) {
            $query->where('floor_id', (int) $filters['floor_id']);
        }
    }

    private function transformAlertData($alert): array
    {
        return [
            'id' => $alert->id,
            'event_type' => $alert->event_type,
            'severity' => $alert->severity,
            'floor_id' => $alert->floor_id,
            'camera_id' => $alert->camera_id,
            'camera_name' => $alert->camera_name ?? "Camera {$alert->camera_id}",
            'room' => $alert->room,
            'confidence' => $alert->confidence,
            'fire_type' => $alert->fire_type ?? $alert->event_type,
            'screenshot_path' => $alert->screenshot_url,
            'screenshot_url' => $alert->screenshot_url,
            'image' => $alert->image,
            'detected_at' => $alert->detected_at,
            'status' => $alert->status,
            'resolved' => in_array($alert->status, ['resolved', 'false_alarm']),
            'resolved_at' => $alert->resolved_at,
            'created_at' => $alert->created_at,
        ];
    }

    private function prepareFireAlertData(array $data): array
    {
        return [
            'event_type' => 'fire',
            'severity' => $data['severity'] ?? 'warning',
            'floor_id' => $data['floor_id'],
            'camera_id' => $data['camera_id'],
            'camera_name' => $data['camera_name'],
            'room' => $data['room'],
            'confidence' => $data['confidence'],
            'fire_type' => $data['fire_type'] ?? 'fire',
            'screenshot_path' => $data['screenshot_path'],
            'image' => $data['image'],
            'detected_at' => $data['detected_at'] ?? now(),
            'status' => 'active',
        ];
    }
}

