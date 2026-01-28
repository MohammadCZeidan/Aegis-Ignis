<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Sensor extends Model
{
    use HasFactory;

    protected $fillable = [
       'floor_id',
       'sensor_type',
       'location_x',
       'location_y',
       'is_active',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'location_x' => 'float',
        'location_y' => 'float',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function floor()
    {
        return $this->belongsTo(Floor::class);
    }
}

