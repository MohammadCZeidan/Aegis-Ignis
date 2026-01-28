<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Floor extends Model
{
    use HasFactory;

    protected $fillable = [
       'building_id',
       'floor_number',
       'name',
    ];

    protected $casts = [
       'created_at' => 'datetime',
       'updated_at' => 'datetime',
    ];

    public function building()
    {
        return $this->belongsTo(Building::class);
    }

    public function cameras()
    {
        return $this->hasMany(Camera::class);
    }

    public function sensors()
    {
        return $this->hasMany(Sensor::class);
    }

    public function employees()
    {
        return $this->hasMany(Employee::class);
    }
}

