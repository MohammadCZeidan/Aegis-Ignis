<?php

namespace App\Services;

use App\Models\Camera;

class CameraService
{
    /**
     * Get all cameras with optional filtering
     */
    public function getAllCameras(?int $floorId = null)
    {
        $query = Camera::with('floor');

        if ($floorId) {
            $query->where('floor_id', $floorId);
        }

        return $query->get();
    }

    /**
     * Get camera by ID
     */
    public function getCameraById(int $id): array
    {
        $camera = Camera::with('floor')->findOrFail($id);
        
        return [
            'success' => true,
            'data' => $camera
        ];
    }

    /**
     * Create a new camera
     */
    public function createCamera(array $data): Camera
    {
        return Camera::create([
            'floor_id' => $data['floor_id'],
            'name' => $data['name'],
            'rtsp_url' => $data['rtsp_url'],
            'position_x' => $data['position_x'] ?? null,
            'position_y' => $data['position_y'] ?? null,
            'position_z' => $data['position_z'] ?? null,
            'calibration_data' => $data['calibration_data'] ?? null,
            'is_active' => $data['is_active'] ?? true,
        ]);
    }

    /**
     * Update camera
     */
    public function updateCamera(int $id, array $data): Camera
    {
        $camera = Camera::findOrFail($id);
        $camera->update($data);

        return $camera->fresh(['floor']);
    }

    /**
     * Delete camera
     */
    public function deleteCamera(int $id): void
    {
        $camera = Camera::findOrFail($id);
        $camera->delete();
    }
}

