<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class FireEvent extends Model
{
    use HasFactory;

    protected $fillable = [
        'floor_id',
        'camera_id',
        'detection_type',
        'confidence',
        'bounding_box',
        'coordinates',
        'room_location',
        'is_resolved',
    ];

    protected $casts = [
        'bounding_box' => 'array',
        'coordinates' => 'array',
        'confidence' => 'float',
        'is_resolved' => 'boolean',
        'timestamp' => 'datetime',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function floor()
    {
        return $this->belongsTo(Floor::class);
    }

    public function camera()
    {
        return $this->belongsTo(Camera::class);
    }

    public function alerts()
    {
        return $this->hasMany(Alert::class, 'fire_event_id');
    }
}

