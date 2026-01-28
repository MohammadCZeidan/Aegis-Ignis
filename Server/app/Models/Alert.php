<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Alert extends Model
{
    use HasFactory;

    protected $fillable = [
       'event_type',
       'floor_id',
       'fire_event_id',
       'severity',
       'status',
       'resolved_at',
       'camera_id',
       'camera_name',
       'room',
       'confidence',
       'fire_type',
       'screenshot_path',
       'image', // Add support for base64 image data
       'detected_at',
    ];

    protected $casts = [
        'resolved_at' => 'datetime',
        'detected_at' => 'datetime',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
        'confidence' => 'float',
    ];

    protected $appends = ['screenshot_url'];

    public function floor()
    {
        return $this->belongsTo(Floor::class);
    }

    public function fireEvent()
    {
        return $this->belongsTo(FireEvent::class);
    }

    public function getScreenshotUrlAttribute(): ?string
    {
        if (!$this->screenshot_path) {
            return null;
        }
        
        // If it already starts with http, return as is
        if (str_starts_with($this->screenshot_path, 'http')) {
            return $this->screenshot_path;
        }
        
        // If it starts with storage/, just prepend APP_URL
        if (str_starts_with($this->screenshot_path, 'storage/')) {
            return url($this->screenshot_path);
        }
        
        // Otherwise, assume it needs /storage/ prepended
        return url('storage/' . ltrim($this->screenshot_path, '/'));
    }
}

