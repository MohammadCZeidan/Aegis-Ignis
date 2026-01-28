<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class RegisterFaceEmbeddingRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
           'embedding' => 'nullable|array',
           'confidence' => 'required|numeric|min:0|max:1',
           'bbox' => 'nullable|array',
           'image_data' => 'required|string',
           'floor_id' => 'required|exists:floors,id',
           'room_location' => 'required|string'
        ];
    }
}
