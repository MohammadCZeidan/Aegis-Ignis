<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class OccupancySnapshot extends Model
{
    use HasFactory;

    protected $fillable = [
        'floor_id',
        'person_count',
        'people_list',
    ];

    protected $casts = [
        'people_list' => 'array',
        'timestamp' => 'datetime',
        'created_at' => 'datetime',
        'updated_at' => 'datetime',
    ];

    public function floor()
    {
        return $this->belongsTo(Floor::class);
    }
}

