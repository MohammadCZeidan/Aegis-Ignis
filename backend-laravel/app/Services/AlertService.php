<?php

namespace App\Services;

use App\Models\Alert;

class AlertService
{
    /**
     * Get all alerts with optional filtering
     */
    public function getAllAlerts(?string $status = null, ?string $eventType = null, ?int $floorId = null)
    {
        $query = Alert::with(['floor', 'fireEvent']);

        if ($status) {
            $query->where('status', $status);
        }

        if ($eventType) {
            $query->where('event_type', $eventType);
        }

        if ($floorId) {
            $query->where('floor_id', $floorId);
        }

        return $query->orderBy('created_at', 'desc')->get();
    }

    /**
     * Get alert by ID
     */
    public function getAlertById(int $id): Alert
    {
        return Alert::with(['floor', 'fireEvent'])->findOrFail($id);
    }

    /**
     * Acknowledge alert
     */
    public function acknowledgeAlert(int $id, string $acknowledgedBy): Alert
    {
        $alert = Alert::findOrFail($id);
        $alert->update([
            'status' => 'acknowledged',
        ]);

        return $alert;
    }
}

