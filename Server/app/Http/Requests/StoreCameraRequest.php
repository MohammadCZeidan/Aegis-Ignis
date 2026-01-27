<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreCameraRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return $this->user()->role === 'admin';
    }

    /**
     * Get the validation rules that apply to the request.
     */
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

