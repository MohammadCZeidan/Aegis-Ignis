<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Employee extends Model
{
    use HasFactory;

    protected $fillable = [
       'name',
       'employee_number',
       'department',
       'email',
       'password',
       'role',
       'status',
       'floor_id',
       'current_floor_id',
       'current_room',
       'face_embedding',
       'face_photo_path',
       'face_registered_at',
       'face_match_confidence',
       'photo_url',
       'last_seen_at'
    ];

    protected $hidden = [
        'password',
    ];

    protected $casts = [
        'face_embedding' => 'array',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    protected $appends = [
        'photo_url',
    ];

    /**
     * Get the photo URL accessor
     */
    public function getPhotoUrlAttribute()
    {
        if ($this->face_photo_path) {
            return url('storage/' . $this->face_photo_path);
        }
        return null;
    }

    public function floor()
    {
        return $this->belongsTo(Floor::class);
    }
}

