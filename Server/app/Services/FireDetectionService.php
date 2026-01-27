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
use Illuminate\Support\Collection;

class FireDetectionService
{
    private const MINIMUM_CONFIDENCE_THRESHOLD = 70;
    private const HIGH_CONFIDENCE_THRESHOLD = 0.9;
    private const MEDIUM_CONFIDENCE_THRESHOLD = 0.7;
    private const LOW_CONFIDENCE_THRESHOLD = 0.5;

    public function reportDetection(array $data): array
    {
        $this->validateDetectionData($data);
        
        $camera = Camera::find($data['camera_id']);
        $floorId = $this->determineFloorId($camera, $data);
        $floor = Floor::find($floorId);
        
        $this->logCameraFloorInfo($camera, $floor, $floorId);
        
        $screenshotPath = $this->handleScreenshotStorage($data);
        $peopleList = $this->getPeopleOnFloor($floorId);
        
        $fireEvent = $this->createFireEvent($data, $floorId);
        $alert = $this->createAlert($fireEvent, $data, $floorId, $screenshotPath, $peopleList);
        
        $fireDetectionData = $this->buildFireDetectionData($fireEvent, $data, $camera, $floor, $floorId, $peopleList);
        
        $this->logAndBroadcastDetection($fireDetectionData, $alert);
        
        return [
            'fire_event' => $fireEvent,
            'alert' => $alert,
            'data' => $fireDetectionData,
        ];
    }

    public function getAllFireEvents(?int $floorId = null, ?bool $isResolved = null): Collection
    {
        $query = FireEvent::with(['floor', 'camera', 'alerts']);

        if ($floorId) {
            $query->where('floor_id', $floorId);
        }

        if ($isResolved !== null) {
            $query->where('is_resolved', $isResolved);
        }

        $events = $query->orderBy('created_at', 'desc')->get();

        $events->each(function ($event) {
            $event->people_data = $this->getPeopleDataForEvent($event);
        });

        return $events;
    }

    public function getFireEventById(int $id): FireEvent
    {
        $event = FireEvent::with(['floor', 'camera', 'alerts'])->findOrFail($id);
        $event->people_data = $this->getPeopleDataForEvent($event);

        return $event;
    }

    public function resolveFireEvent(int $id): FireEvent
    {
        $event = FireEvent::findOrFail($id);
        $event->update(['is_resolved' => true]);

        $event->alerts()->update(['status' => 'resolved', 'resolved_at' => now()]);

        return $event;
    }

    private function validateDetectionData(array $data): void
    {
        if ($data['confidence'] < self::MINIMUM_CONFIDENCE_THRESHOLD) {
            Log::warning("Fire detection REJECTED: {$data['confidence']}% < " . self::MINIMUM_CONFIDENCE_THRESHOLD . "%");
            throw new \Exception("Fire detection rejected: Confidence too low ({$data['confidence']}%)");
        }
        
        if ($this->hasNoScreenshot($data)) {
            Log::warning("Fire detection REJECTED: No screenshot provided");
            throw new \Exception("Fire detection rejected: Screenshot required");
        }
        
        Log::info("Fire detection ACCEPTED: {$data['confidence']}% with screenshot");
    }

    private function hasNoScreenshot(array $data): bool
    {
        return empty($data['screenshot_path']) && 
               empty($data['detection_image']) && 
               empty($data['screenshot']);
    }

    private function determineFloorId(?Camera $camera, array $data): int
    {
        return $camera ? $camera->floor_id : $data['floor_id'];
    }

    private function logCameraFloorInfo(?Camera $camera, ?Floor $floor, int $floorId): void
    {
        if (!$camera) {
            Log::warning("Camera not found in database, using floor_id from request", ['camera_id' => $camera->id ?? 'unknown']);
        } else {
            Log::info("Using camera's current floor", ['camera_id' => $camera->id, 'floor_id' => $floorId]);
        }
        
        if (!$floor) {
            Log::warning("Floor not found in database", ['floor_id' => $floorId]);
        }
    }

    private function handleScreenshotStorage(array $data): ?string
    {
        if (isset($data['screenshot_path'])) {
            return $data['screenshot_path'];
        }
        
        if (isset($data['screenshot'])) {
            return $this->storeBase64Screenshot($data['screenshot']);
        }
        
        return null;
    }

    private function storeBase64Screenshot(string $base64Image): string
    {
        $imageData = base64_decode($base64Image);
        $filename = 'alerts/' . time() . '_fire_detection.jpg';
        \Illuminate\Support\Facades\Storage::disk('public')->put($filename, $imageData);
        
        return $filename;
    }

    private function createFireEvent(array $data, int $floorId): FireEvent
    {
        return FireEvent::create([
            'floor_id' => $floorId,
            'camera_id' => $data['camera_id'],
            'detection_type' => $data['detection_type'],
            'confidence' => $data['confidence'],
            'bounding_box' => $data['bounding_box'] ?? null,
            'coordinates' => $data['coordinates'] ?? null,
            'room_location' => $data['room_location'] ?? null,
            'is_resolved' => false,
        ]);
    }

    private function createAlert(FireEvent $fireEvent, array $data, int $floorId, ?string $screenshotPath, array $peopleList): mixed
    {
        return $fireEvent->alerts()->create([
            'event_type' => $data['detection_type'],
            'alert_type' => 'fire_large',
            'floor_id' => $floorId,
            'camera_id' => $data['camera_id'],
            'room_location' => $data['room_location'] ?? null,
            'fire_event_id' => $fireEvent->id,
            'severity' => $this->calculateSeverity($data['confidence'], count($peopleList)),
            'confidence' => $data['confidence'],
            'people_count' => count($peopleList),
            'detected_at' => now(),
            'detection_image_path' => $screenshotPath,
            'screenshot_path' => $screenshotPath,
            'status' => 'active',
        ]);
    }

    private function buildFireDetectionData(FireEvent $fireEvent, array $data, ?Camera $camera, ?Floor $floor, int $floorId, array $peopleList): array
    {
        return [
            'fire_event_id' => $fireEvent->id,
            'floor_id' => $floorId,
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
    }

    private function logAndBroadcastDetection(array $fireDetectionData, $alert): void
    {
        Log::info('Fire Detection Reported', $fireDetectionData);
        
        broadcast(new FireDetected($fireDetectionData))->toOthers();
        broadcast(new AlertCreated($alert))->toOthers();
    }

    protected function getPeopleOnFloor(int $floorId): array
    {
        $currentOccupancy = $this->getCurrentOccupancy($floorId);
        
        if (!$currentOccupancy || !$currentOccupancy->people_list) {
            return [];
        }
        
        return $this->enhancePeopleListWithEmployeeData($currentOccupancy->people_list);
    }

    protected function getPeopleDataForEvent(FireEvent $event): array
    {
        $snapshot = $this->getOccupancySnapshotForEvent($event);

        if (!$snapshot || !$snapshot->people_list) {
            return [
                'total_count' => 0,
                'people' => [],
            ];
        }

        $people = $this->enhancePeopleListWithEmployeeData($snapshot->people_list);

        return [
            'total_count' => count($people),
            'people' => $people,
        ];
    }

    protected function calculateSeverity(float $confidence, int $peopleCount): string
    {
        if ($confidence >= self::HIGH_CONFIDENCE_THRESHOLD && $peopleCount > 0) {
            return 'critical';
        } elseif ($confidence >= self::MEDIUM_CONFIDENCE_THRESHOLD) {
            return 'high';
        } elseif ($confidence >= self::LOW_CONFIDENCE_THRESHOLD) {
            return 'medium';
        }
        
        return 'low';
    }

    private function getCurrentOccupancy(int $floorId): ?OccupancySnapshot
    {
        return OccupancySnapshot::where('floor_id', $floorId)
            ->orderBy('timestamp', 'desc')
            ->first();
    }

    private function getOccupancySnapshotForEvent(FireEvent $event): ?OccupancySnapshot
    {
        return OccupancySnapshot::where('floor_id', $event->floor_id)
            ->where('timestamp', '<=', $event->created_at)
            ->orderBy('timestamp', 'desc')
            ->first();
    }

    private function enhancePeopleListWithEmployeeData(array $peopleList): array
    {
        $employeeIds = collect($peopleList)->pluck('employee_id')->filter()->unique();
        $employees = Employee::whereIn('id', $employeeIds)
            ->with('floor')
            ->get()
            ->keyBy('id');

        return collect($peopleList)->map(function ($person) use ($employees) {
            $personData = $person;
            if (isset($person['employee_id']) && $employees->has($person['employee_id'])) {
                $employee = $employees[$person['employee_id']];
                $personData['name'] = $employee->name;
                $personData['email'] = $employee->email;
            }
            return $personData;
        })->toArray();
    }
}

