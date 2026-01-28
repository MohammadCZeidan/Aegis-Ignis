<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreCameraRequest extends FormRequest
{
    
    public function authorize(): bool
    {
        return $this->user()->role === 'admin';
    }

   
    public function rules(): array
    {
        return [
            'floor_id' => 'required|exists:floors,id',
            'name' => 'required|string|max:255',
            'rtsp_url' => 'required|string',
            'position_x' => 'nullable|numeric',
            'position_y' => 'nullable|numeric',
            'position_z' => 'nullable|numeric',
            'calibration_data' => 'nullable|array',
            'is_active' => 'boolean',
        ];
    }
}

