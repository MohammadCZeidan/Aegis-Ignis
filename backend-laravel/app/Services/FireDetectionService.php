<?php

namespace App\Services;

use App\Models\FireEvent;
use App\Models\Floor;
use App\Models\Camera;
use App\Models\Employee;
use App\Models\OccupancySnapshot;
use App\Events\FireDetected;
use App\Events\AlertCreated;
use Illuminate\Support\Facades\Log;

class FireDetectionService
{
    /**
     * Report fire detection
     */
    public function reportDetection(array $data): array
    {
        // ========================================
        // VALIDATION: Prevent fake fire alerts!
        // ========================================
        
        // 1. Reject low confidence detections
        $minConfidence = 70; // Require 70%+ confidence (was 60%)
        if ($data['confidence'] < $minConfidence) {
            \Log::warning("🚫 Fire detection REJECTED: {$data['confidence']}% < {$minConfidence}%");
            throw new \Exception("Fire detection rejected: Confidence too low ({$data['confidence']}%)");
        }
        
        // 2. Require screenshot (no screenshot = likely fake)
        if (empty($data['screenshot_path']) && empty($data['detection_image']) && empty($data['screenshot'])) {
            \Log::warning("🚫 Fire detection REJECTED: No screenshot provided");
            throw new \Exception("Fire detection rejected: Screenshot required");
        }
        
        \Log::info("✅ Fire detection ACCEPTED: {$data['confidence']}% with screenshot");
        
        // Find camera and get its CURRENT floor location
        $camera = Camera::find($data['camera_id']);
        
        // IMPORTANT: Use camera's current floor_id from database, not from request
        // This ensures alerts reflect the camera's updated location
        $floorId = $camera ? $camera->floor_id : $data['floor_id'];
        $floor = Floor::find($floorId);

        // Log if camera/floor not found
        if (!$camera) {
            Log::warning("Camera not found in database, using floor_id from request", ['camera_id' => $data['camera_id']]);
        } else {
            Log::info("Using camera's current floor", ['camera_id' => $camera->id, 'floor_id' => $floorId]);
        }
        if (!$floor) {
            Log::warning("Floor not found in database", ['floor_id' => $floorId]);
        }

        // Save screenshot if provided (base64 or path)
        $screenshotPath = null;
        if (isset($data['screenshot_path'])) {
            // Direct file path provided by service
            $screenshotPath = $data['screenshot_path'];
        } elseif (isset($data['screenshot'])) {
            // Base64 encoded image
            $imageData = base64_decode($data['screenshot']);
            $filename = 'alerts/' . time() . '_fire_detection.jpg';
            \Illuminate\Support\Facades\Storage::disk('public')->put($filename, $imageData);
            $screenshotPath = $filename;
        }

        // Get current people on this floor (use the camera's current floor)
        $peopleList = $this->getPeopleOnFloor($floorId);

        // Create fire event with camera's current floor
        $fireEvent = FireEvent::create([
            'floor_id' => $floorId,  // Use camera's current floor
            'camera_id' => $data['camera_id'],
            'detection_type' => $data['detection_type'],
            'confidence' => $data['confidence'],
            'bounding_box' => $data['bounding_box'] ?? null,
            'coordinates' => $data['coordinates'] ?? null,
            'room_location' => $data['room_location'] ?? null,
            'is_resolved' => false,
        ]);

        // Create alert with ALL required fields including screenshot_path
        $alert = $fireEvent->alerts()->create([
            'event_type' => $data['detection_type'],
            'alert_type' => 'fire_large', // Map detection_type to alert_type
            'floor_id' => $floorId,  // Use camera's current floor
            'camera_id' => $data['camera_id'],
            'room_location' => $data['room_location'] ?? null,
            'fire_event_id' => $fireEvent->id,
            'severity' => $this->calculateSeverity($data['confidence'], count($peopleList)),
            'confidence' => $data['confidence'], // ADD confidence
            'people_count' => count($peopleList), // ADD people count
            'detected_at' => now(), // ADD detection timestamp
            'detection_image_path' => $screenshotPath, // ADD screenshot
            'screenshot_path' => $screenshotPath, // ALSO save to screenshot_path column
            'status' => 'active',
        ]);

        // Prepare fire detection data
        $fireDetectionData = [
            'fire_event_id' => $fireEvent->id,
            'floor_id' => $floorId,  // Use camera's current floor
            'floor_name' => $floor ? $floor->name : "Floor " . $floorId,
            'room_location' => $data['room_location'] ?? 'Unknown',
            'camera_id' => $data['camera_id'],
            'camera_name' => $camera ? $camera->name : "Camera " . $data['camera_id'],
            'detection_type' => $data['detection_type'],
            'confidence' => $data['confidence'],
            'timestamp' => $fireEvent->created_at->toISOString(),
            'people_on_floor' => [
                'total_count' => count($peopleList),
                'people' => $peopleList,
            ],
        ];

        // Log the detection
        Log::info('Fire Detection Reported', $fireDetectionData);

        // Broadcast real-time events (pass the data array, not the model)
        broadcast(new FireDetected($fireDetectionData))->toOthers();
        broadcast(new AlertCreated($alert))->toOthers();

        return [
            'fire_event' => $fireEvent,
            'alert' => $alert,
            'data' => $fireDetectionData,
        ];
    }

    /**
     * Get all fire events with optional filtering
     */
    public function getAllFireEvents(?int $floorId = null, ?bool $isResolved = null)
    {
        $query = FireEvent::with(['floor', 'camera', 'alerts']);

        if ($floorId) {
            $query->where('floor_id', $floorId);
        }

        if ($isResolved !== null) {
            $query->where('is_resolved', $isResolved);
        }

        $events = $query->orderBy('created_at', 'desc')->get();

        // Add people data to each event
        $events->each(function ($event) {
            $event->people_data = $this->getPeopleDataForEvent($event);
        });

        return $events;
    }

    /**
     * Get fire event by ID
     */
    public function getFireEventById(int $id): FireEvent
    {
        $event = FireEvent::with(['floor', 'camera', 'alerts'])->findOrFail($id);
        $event->people_data = $this->getPeopleDataForEvent($event);

        return $event;
    }

    /**
     * Resolve fire event
     */
    public function resolveFireEvent(int $id): FireEvent
    {
        $event = FireEvent::findOrFail($id);
        $event->update(['is_resolved' => true]);

        // Resolve related alerts
        $event->alerts()->update(['status' => 'resolved', 'resolved_at' => now()]);

        return $event;
    }

    /**
     * Get people currently on floor
     */
    protected function getPeopleOnFloor(int $floorId): array
    {
        $currentOccupancy = OccupancySnapshot::where('floor_id', $floorId)
            ->orderBy('timestamp', 'desc')
            ->first();

        $peopleOnFloor = [];
        if ($currentOccupancy && $currentOccupancy->people_list) {
            $peopleOnFloor = $currentOccupancy->people_list;
        }

        // Get employee details for people on floor
        $employeeIds = collect($peopleOnFloor)->pluck('employee_id')->filter()->unique();
        $employees = Employee::whereIn('id', $employeeIds)
            ->with('floor')
            ->get()
            ->keyBy('id');

        // Enhance people list with employee names
        return collect($peopleOnFloor)->map(function ($person) use ($employees) {
            $personData = $person;
            if (isset($person['employee_id']) && $employees->has($person['employee_id'])) {
                $employee = $employees[$person['employee_id']];
                $personData['name'] = $employee->name;
                $personData['email'] = $employee->email;
            }
            return $personData;
        })->toArray();
    }

    /**
     * Get people data for a fire event
     */
    protected function getPeopleDataForEvent(FireEvent $event): array
    {
        // Get occupancy snapshot closest to fire event time
        $snapshot = OccupancySnapshot::where('floor_id', $event->floor_id)
            ->where('timestamp', '<=', $event->created_at)
            ->orderBy('timestamp', 'desc')
            ->first();

        if (!$snapshot || !$snapshot->people_list) {
            return [
                'total_count' => 0,
                'people' => [],
            ];
        }

        $employeeIds = collect($snapshot->people_list)->pluck('employee_id')->filter()->unique();
        $employees = Employee::whereIn('id', $employeeIds)->get()->keyBy('id');

        $people = collect($snapshot->people_list)->map(function ($person) use ($employees) {
            $personData = $person;
            if (isset($person['employee_id']) && $employees->has($person['employee_id'])) {
                $employee = $employees[$person['employee_id']];
                $personData['name'] = $employee->name;
                $personData['email'] = $employee->email;
            }
            return $personData;
        })->toArray();

        return [
            'total_count' => count($people),
            'people' => $people,
        ];
    }

    /**
     * Calculate alert severity based on confidence and people count
     */
    protected function calculateSeverity(float $confidence, int $peopleCount): string
    {
        if ($confidence >= 0.9 && $peopleCount > 0) {
            return 'critical';
        } elseif ($confidence >= 0.7) {
            return 'high';
        } elseif ($confidence >= 0.5) {
            return 'medium';
        }
        return 'low';
    }
}

