<?php

namespace App\Services;

use App\Models\Camera;
use Illuminate\Database\Eloquent\Collection;

class CameraService
{
    public function getAllCameras(?int $floorId = null): Collection
    {
        $query = Camera::with('floor');

        if ($floorId) {
            $query->where('floor_id', $floorId);
        }

        return $query->get();
    }

    public function getCameraById(int $id): array
    {
        $camera = Camera::with('floor')->findOrFail($id);
          return [
            'success' => true,
            'data' => $camera
        ];
    }

    public function createCamera(array $data): Camera
    {
        $cameraData = $this->prepareCameraData($data);
        return Camera::create($cameraData);
    }

    public function updateCamera(int $id, array $data): Camera
    {
        $camera = Camera::findOrFail($id);
        $camera->update($data);

        return $camera->fresh(['floor']);
    }

    public function updateCameraFloor(int $cameraId, int $newFloorId): array
    {
        $camera = $this->updateCamera($cameraId, ['floor_id' => $newFloorId]);
        
        return [
            'success' => true,
            'message' => "Camera floor updated to {$camera->floor->name}",
            'camera' => $camera
        ];
    }

    public function deleteCamera(int $id): void
    {
        $camera = Camera::findOrFail($id);
        $camera->delete();
    }

    private function prepareCameraData(array $data): array
    {
        return [
            'floor_id' => $data['floor_id'],
            'name' => $data['name'],
            'rtsp_url' => $data['rtsp_url'],
            'position_x' => $data['position_x'] ?? null,
            'position_y' => $data['position_y'] ?? null,
            'position_z' => $data['position_z'] ?? null,
            'calibration_data' => $data['calibration_data'] ?? null,
            'is_active' => $data['is_active'] ?? true,
        ];
    }
}

