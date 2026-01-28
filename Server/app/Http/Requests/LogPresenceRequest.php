<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class LogPresenceRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
           'employee_id' => 'required|exists:employees,id',
           'floor_id' => 'nullable|exists:floors,id',
           'room_location' => 'nullable|string',
           'camera_id' => 'nullable|string',
           'confidence' => 'required|numeric|min:0|max:100',
           'detection_image' => 'nullable|string',
           'event_type' => 'nullable|in:entry,exit,movement,detected'
        ];
    }
}
