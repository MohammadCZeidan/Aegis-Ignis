<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Camera extends Model
{
    use HasFactory;

    protected $fillable = [
       'floor_id',
       'name',
       'rtsp_url',
       'position_x',
       'position_y',
       'position_z',
       'calibration_data',
       'is_active',
    ];

    protected $casts = [
        'calibration_data' => 'array',
        'is_active' => 'boolean',
        'position_x' => 'float',
        'position_y' => 'float',
        'position_z' => 'float',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function floor()
    {
        return $this->belongsTo(Floor::class);
    }
}

