<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class CreateFireAlertRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
            'alert_type' => 'required|in:fire_smoke,fire_small,fire_large,evacuation',
            'severity' => 'required|in:warning,alert,critical',
            'floor_id' => 'nullable|exists:floors,id',
            'room_location' => 'nullable|string',
            'camera_id' => 'nullable|string',
            'confidence' => 'required|numeric|min:0|max:100',
            'description' => 'required|string',
            'detection_image' => 'nullable|string',
            'metadata' => 'nullable|array'
        ];
    }
}
