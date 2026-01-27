<?php

namespace App\Services;

use App\Models\Floor;

class FloorService
{
    /**
     * Get all floors
     */
    public function getAllFloors()
    {
        return Floor::with('building')->get();
    }

    /**
     * Get floor by ID with relations
     */
    public function getFloorById(int $id)
    {
        return Floor::with(['building', 'cameras', 'sensors', 'employees'])->findOrFail($id);
    }

    /**
     * Create a new floor
     */
    public function createFloor(array $data): Floor
    {
        return Floor::create([
            'building_id' => $data['building_id'],
            'floor_number' => $data['floor_number'],
            'name' => $data['name'] ?? null,
        ]);
    }

    /**
     * Update floor
     */
    public function updateFloor(int $id, array $data): Floor
    {
        $floor = Floor::findOrFail($id);
        $floor->update($data);

        return $floor->fresh(['building']);
    }

    /**
     * Delete floor
     */
    public function deleteFloor(int $id): void
    {
        $floor = Floor::findOrFail($id);
        $floor->delete();
    }
}

