<?php

namespace App\Services;

use App\Models\EmergencyAlert;
use App\Models\Employee;
use App\Models\Floor;
use Illuminate\Support\Facades\Storage;

class EmergencyService
{
    public function createFireAlert(array $data): ?EmergencyAlert
    {
        if ($data['confidence'] < 30) {
            logger()->info('Rejected low confidence detection', [
                'confidence' => $data['confidence'],
                'camera_id' => $data['camera_id'] ?? null
            ]);
            
            return null;
        }

        $imagePath = null;
        if (isset($data['detection_image'])) {
            $imagePath = $this->storeAlertImage($data['detection_image']);
        }

        $affectedEmployees = [];
        $peopleCount = 0;
        
        if ($data['floor_id']) {
            $affectedEmployees = Employee::where('current_floor_id', $data['floor_id'])
                ->where('presence_status', 'in_building')
                ->pluck('id')
                ->toArray();
            $peopleCount = count($affectedEmployees);
        }

        $aiMessage = $this->generateAIMessage(
            $data['alert_type'],
            $data['severity'],
            $data['floor_id'],
            $peopleCount
        );

        $alert = EmergencyAlert::create([
            'alert_type' => $data['alert_type'],
            'severity' => $data['severity'],
            'floor_id' => $data['floor_id'] ?? null,
            'room_location' => $data['room_location'] ?? null,
            'camera_id' => $data['camera_id'] ?? null,
            'description' => $data['description'],
            'detection_image_path' => $imagePath,
            'confidence' => $data['confidence'],
            'people_count' => $peopleCount,
            'affected_employees' => $affectedEmployees,
            'detected_at' => now(),
            'ai_message' => $aiMessage,
            'status' => 'active'
        ]);

        if ($data['severity'] === 'critical' && $peopleCount > 0) {
            $this->notifyPolice($alert);
        }

        return $alert;
    }

    public function getActiveAlerts(?int $perPage = 10)
    {
        $alerts = EmergencyAlert::where('status', 'active')
            ->with('floor')
            ->orderBy('severity', 'desc')
            ->orderBy('detected_at', 'desc')
            ->get();
            
        $formatted = $alerts->map(function ($alert) {
            return $this->formatActiveAlert($alert);
        });
        
        return [
            'data' => $formatted,
            'total' => $formatted->count()
        ];
    }

    public function getAlertHistory(?int $perPage = 15, ?string $severity = null, ?int $floorId = null)
    {
        $query = EmergencyAlert::with('floor');

        if ($severity) {
            $query->where('severity', $severity);
        }

        if ($floorId) {
            $query->where('floor_id', $floorId);
        }

        $alerts = $query->orderBy('detected_at', 'desc')->get();
        
        $formatted = $alerts->map(function ($alert) {
            return $this->formatAlertHistory($alert);
        });
        
        return [
            'data' => $formatted,
            'total' => $formatted->count()
        ];
    }

    public function acknowledgeAlert(int $id): EmergencyAlert
    {
        $alert = EmergencyAlert::findOrFail($id);
        $alert->update([
            'status' => 'acknowledged',
            'acknowledged_at' => now()
        ]);

        return $alert;
    }

    public function resolveAlert(int $id, bool $isFalseAlarm = false): EmergencyAlert
    {
        $alert = EmergencyAlert::findOrFail($id);
        $alert->update([
            'status' => $isFalseAlarm ? 'false_alarm' : 'resolved',
            'resolved_at' => now()
        ]);

        return $alert;
    }

    public function formatActiveAlert($alert): array
    {
        return [
            'id' => $alert->id,
            'alert_type' => $alert->alert_type,
            'severity' => $alert->severity,
            'floor' => $alert->floor?->name,
            'floor_id' => $alert->floor_id,
            'room_location' => $alert->room_location,
            'camera_id' => $alert->camera_id,
            'description' => $alert->description,
            'confidence' => $alert->confidence,
            'people_count' => $alert->people_count,
            'detected_at' => $alert->detected_at->diffForHumans(),
            'detected_timestamp' => $alert->detected_at,
            'image_url' => $alert->detection_image_path 
                ? url(Storage::url($alert->detection_image_path))
                : null,
            'police_notified' => $alert->police_notified,
            'ai_message' => $alert->ai_message,
            'status' => $alert->status,
            'affected_people' => $alert->getAffectedEmployeeModels()->map(function ($emp) {
                return [
                    'id' => $emp->id,
                    'name' => $emp->name,
                    'photo_url' => $emp->face_photo_path 
                        ? url(Storage::url($emp->face_photo_path))
                        : null,
                ];
            })
        ];
    }

    public function formatAlertHistory($alert): array
    {
        return [
            'id' => $alert->id,
            'alert_type' => $alert->alert_type,
            'severity' => $alert->severity,
            'floor' => $alert->floor?->name,
            'room_location' => $alert->room_location,
            'description' => $alert->description,
            'people_count' => $alert->people_count,
            'detected_at' => $alert->detected_at,
            'resolved_at' => $alert->resolved_at,
            'status' => $alert->status,
            'police_notified' => $alert->police_notified,
            'image_url' => $alert->detection_image_path 
                ? url(Storage::url($alert->detection_image_path))
                : null,
        ];
    }

    private function storeAlertImage(string $imageData): string
    {
        $decodedImage = base64_decode($imageData);
        $filename = 'alerts/' . time() . '_fire_detection.jpg';
        Storage::disk('public')->put($filename, $decodedImage);
        
        return $filename;
    }

    private function generateAIMessage(string $alertType, string $severity, ?int $floorId, int $peopleCount): string
    {
        $floorName = $floorId ? Floor::find($floorId)?->name : 'unknown floor';
        
        $messages = [
            'fire_smoke' => [
                'warning' => "Attention: Smoke has been detected on {$floorName}. {$peopleCount} people are in the affected area. Please remain alert and prepare for possible evacuation.",
                'alert' => "ALERT: Significant smoke detected on {$floorName}. {$peopleCount} people are at risk. Begin evacuation procedures immediately.",
                'critical' => "CRITICAL: Heavy smoke on {$floorName}! {$peopleCount} people in danger. Emergency evacuation in progress. All exits must be cleared immediately!"
            ],
            'fire_small' => [
                'warning' => "Fire warning: Small flames detected on {$floorName}. {$peopleCount} people in vicinity. Fire suppression teams notified.",
                'alert' => "FIRE ALERT: Active flames on {$floorName}. {$peopleCount} people at risk. Evacuate the floor immediately!",
                'critical' => "CRITICAL FIRE: Rapidly spreading flames on {$floorName}! {$peopleCount} people in immediate danger. Full building evacuation ordered!"
            ],
            'fire_large' => [
                'critical' => "CRITICAL EMERGENCY: Large fire on {$floorName}! {$peopleCount} people in extreme danger. Emergency services dispatched. Complete evacuation in progress!"
            ]
        ];

        return $messages[$alertType][$severity] ?? "Emergency alert: {$alertType} - {$severity} on {$floorName}";
    }

    private function notifyPolice(EmergencyAlert $alert): void
    {
        logger()->critical('EMERGENCY: Police notification', [
            'alert_id' => $alert->id,
            'type' => $alert->alert_type,
            'severity' => $alert->severity,
            'floor' => $alert->floor?->name,
            'room' => $alert->room_location,
            'people_affected' => $alert->people_count,
            'message' => $alert->ai_message
        ]);

        $alert->update([
            'police_notified' => true,
            'police_notified_at' => now()
        ]);

        $this->sendAIVoiceAlert($alert);
    }

    private function sendAIVoiceAlert(EmergencyAlert $alert): void
    {
        logger()->info('AI Voice Alert', [
            'message' => $alert->ai_message,
            'phone_numbers' => ['emergency_services', 'building_security']
        ]);
    }
}
