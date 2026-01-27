<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class EmergencyAlert extends Model
{
    protected $fillable = [
        'alert_type',
        'severity',
        'floor_id',
        'room_location',
        'camera_id',
        'description',
        'detection_image_path',
        'confidence',
        'people_count',
        'affected_employees',
        'detected_at',
        'acknowledged_at',
        'resolved_at',
        'police_notified',
        'police_notified_at',
        'ai_message',
        'status'
    ];

    protected $casts = [
        'detected_at' => 'datetime',
        'acknowledged_at' => 'datetime',
        'resolved_at' => 'datetime',
        'police_notified_at' => 'datetime',
        'police_notified' => 'boolean',
        'affected_employees' => 'array',
        'confidence' => 'decimal:2',
        'people_count' => 'integer'
    ];

    protected $appends = ['detection_image_url'];

    public function floor(): BelongsTo
    {
        return $this->belongsTo(Floor::class);
    }

    public function getDetectionImageUrlAttribute(): ?string
    {
        if (!$this->detection_image_path) {
            return null;
        }
        
        // If path starts with http, return as is
        if (str_starts_with($this->detection_image_path, 'http')) {
            return $this->detection_image_path;
        }
        
        // Otherwise generate storage URL
        return \Storage::url($this->detection_image_path);
    }

    public function getAffectedEmployeeModels()
    {
        if (!$this->affected_employees) {
            return collect();
        }
        return Employee::whereIn('id', $this->affected_employees)->get();
    }
}
