<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Services\OccupancyService;

class OccupancyController extends Controller
{
    protected OccupancyService $occupancyService;

    public function __construct(OccupancyService $occupancyService)
    {
        $this->occupancyService = $occupancyService;
    }

    /**
     * Get occupancy summary
     */
    public function summary()
    {
        $summary = $this->occupancyService->getSummary();

        return response()->json($summary);
    }

    /**
     * Get occupancy by floor
     */
    public function byFloor($floorId)
    {
        $occupancy = $this->occupancyService->getByFloor((int) $floorId);

        return response()->json($occupancy);
    }
}

