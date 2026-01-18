<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class PresenceLog extends Model
{
    protected $fillable = [
        'employee_id',
        'floor_id',
        'room_location',
        'camera_id',
        'confidence',
        'detection_image_path',
        'event_type',
        'detected_at',
        'metadata'
    ];

    protected $casts = [
        'detected_at' => 'datetime',
        'metadata' => 'array',
        'confidence' => 'decimal:2'
    ];

    public function employee(): BelongsTo
    {
        return $this->belongsTo(Employee::class);
    }

    public function floor(): BelongsTo
    {
        return $this->belongsTo(Floor::class);
    }
}
