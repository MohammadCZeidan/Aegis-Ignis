<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class UpdateCameraRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        // Allow if user is admin OR if user is authenticated (for settings updates)
        return $this->user() && ($this->user()->role === 'admin' || auth()->check());
    }

    /**
     * Get the validation rules that apply to the request.
     */
    public function rules(): array
    {
        return [
            'floor_id' => 'sometimes|exists:floors,id',
            'name' => 'sometimes|string|max:255',
            'rtsp_url' => 'sometimes|string',
            'room' => 'sometimes|nullable|string|max:255',
            'position_x' => 'nullable|numeric',
            'position_y' => 'nullable|numeric',
            'position_z' => 'nullable|numeric',
            'calibration_data' => 'nullable|array',
            'is_active' => 'sometimes|boolean',
        ];
    }
}

