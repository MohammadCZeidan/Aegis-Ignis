<?php

namespace App\Services;

use App\Models\OccupancySnapshot;

class OccupancyService
{
    /**
     * Get occupancy summary across all floors
     */
    public function getSummary(): array
    {
        $floors = OccupancySnapshot::selectRaw('floor_id, SUM(person_count) as person_count')
            ->groupBy('floor_id')
            ->get();

        $total = $floors->sum('person_count');

        return [
            'total_occupancy' => $total,
            'floors' => $floors->map(function ($floor) {
                return [
                    'floor_id' => $floor->floor_id,
                    'person_count' => $floor->person_count,
                ];
            }),
        ];
    }

   
    public function getByFloor(int $floorId): array
    {
        $snapshot = OccupancySnapshot::where('floor_id', $floorId)
            ->orderBy('timestamp', 'desc')
            ->first();

        if (!$snapshot) {
            return [
                'floor_id' => $floorId,
                'person_count' => 0,
                'people_list' => [],
                'timestamp' => now()->toISOString(),
            ];
        }

        return [
            'floor_id' => $snapshot->floor_id,
            'person_count' => $snapshot->person_count,
            'people_list' => $snapshot->people_list,
            'timestamp' => $snapshot->timestamp->toISOString(),
        ];
    }
}

