<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Alert;
use App\Models\EmergencyAlert;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;

class AlertController extends Controller
{
    /**
     * List all alerts - Check both Alert and EmergencyAlert tables
     */
    public function index(Request $request)
    {
        try {
            // Try Alert table first (where fire detection creates alerts)
            $query = Alert::query();

            if ($request->has('status')) {
                $query->where('status', $request->status);
            }

            if ($request->has('event_type')) {
                $query->where('event_type', $request->event_type);
            }

            if ($request->has('floor_id')) {
                $query->where('floor_id', (int) $request->floor_id);
            }

            $alerts = $query->orderBy('created_at', 'desc')
                ->get()
                ->map(function ($alert) {
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
                        'screenshot_path' => $alert->screenshot_url,  // Use accessor
                        'screenshot_url' => $alert->screenshot_url,    // Also provide screenshot_url
                        'detected_at' => $alert->detected_at,
                        'status' => $alert->status,
                        'resolved' => in_array($alert->status, ['resolved', 'false_alarm']),
                        'resolved_at' => $alert->resolved_at,
                        'created_at' => $alert->created_at,
                    ];
                });

            return response()->json([
                'success' => true,
                'alerts' => $alerts
            ]);
        } catch (\Exception $e) {
            Log::error('Failed to fetch alerts', ['error' => $e->getMessage()]);
            return response()->json([
                'success' => true,
                'alerts' => []
            ]);
        }
    }

    /**
     * Get alert details
     */
    public function show($id)
    {
        try {
            $alert = Alert::findOrFail($id);
            return response()->json([
                'success' => true,
                'alert' => $alert
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'Alert not found'
            ], 404);
        }
    }

    /**
     * Acknowledge alert - marks it as resolved and inactive
     */
    public function acknowledge(Request $request, $id)
    {
        try {
            $alert = Alert::findOrFail($id);
            $alert->update([
                'status' => 'resolved',  // Mark as resolved to move to history
                'resolved' => true,       // Mark as inactive
                'resolved_at' => now()
            ]);

            return response()->json([
                'success' => true,
                'message' => 'Alert acknowledged and resolved',
                'alert' => $alert
            ]);
        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'Failed to acknowledge alert: ' . $e->getMessage()
            ], 500);
        }
    }

    /**
     * Create fire alert from camera detection service
     */
    public function createFireAlert(Request $request)
    {
        try {
            $alert = Alert::create([
                'event_type' => 'fire',
                'severity' => $request->input('severity', 'warning'),
                'floor_id' => $request->input('floor_id'),
                'camera_id' => $request->input('camera_id'),
                'camera_name' => $request->input('camera_name'),
                'room' => $request->input('room'),
                'confidence' => $request->input('confidence'),
                'fire_type' => $request->input('fire_type', 'fire'),
                'screenshot_path' => $request->input('screenshot_path'),
                'detected_at' => $request->input('detected_at', now()),
                'status' => 'active',
            ]);

            Log::info('Fire alert created', [
                'alert_id' => $alert->id,
                'camera' => $request->input('camera_name'),
                'floor' => $request->input('floor_id')
            ]);

            return response()->json([
                'success' => true,
                'alert' => $alert
            ], 201);

        } catch (\Exception $e) {
            Log::error('Failed to create fire alert', [
                'error' => $e->getMessage(),
                'request' => $request->all()
            ]);

            return response()->json([
                'success' => false,
                'error' => 'Failed to create alert'
            ], 500);
        }
    }

    /**
     * Get alerts by floor
     */
    public function byFloor($floorId)
    {
        try {
            $alerts = Alert::where('floor_id', $floorId)
                ->orderBy('created_at', 'desc')
                ->get()
                ->map(function ($alert) {
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
                        'screenshot_path' => $alert->screenshot_url,  // Use accessor for full URL
                        'screenshot_url' => $alert->screenshot_url,    // Also provide screenshot_url
                        'detected_at' => $alert->detected_at,
                        'status' => $alert->status,
                        'resolved' => in_array($alert->status, ['resolved', 'false_alarm']),
                        'resolved_at' => $alert->resolved_at,
                        'created_at' => $alert->created_at,
                    ];
                });

            return response()->json($alerts);

        } catch (\Exception $e) {
            return response()->json([
                'success' => false,
                'error' => 'Failed to fetch alerts'
            ], 500);
        }
    }
}
