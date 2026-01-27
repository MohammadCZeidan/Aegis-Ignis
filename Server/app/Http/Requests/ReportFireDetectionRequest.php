<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class ReportFireDetectionRequest extends FormRequest
{
    /**
     * Determine if the user is authorized to make this request.
     */
    public function authorize(): bool
    {
        return true; // Public endpoint for fire detection service
    }

    /**
     * Get the validation rules that apply to the request.
     */
    public function rules(): array
    {
        return [
            'camera_id' => 'required|exists:cameras,id',
            'floor_id' => 'required|exists:floors,id',
            'detection_type' => 'required|in:fire,smoke',
            'confidence' => 'required|numeric|min:0|max:100', // Changed to 0-100
            'room_location' => 'nullable|string|max:255',
            'screenshot' => 'nullable|string', // base64 encoded image
            'screenshot_path' => 'nullable|string', // file path to screenshot
            'bounding_box' => 'nullable|array',
            'coordinates' => 'nullable|array',
        ];
    }
}

