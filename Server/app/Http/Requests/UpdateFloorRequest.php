<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class UpdateFloorRequest extends FormRequest
{
    
    public function authorize(): bool
    {
        return $this->user()->role === 'admin';
    }

    
    public function rules(): array
    {
        return [
            'building_id' => 'sometimes|exists:buildings,id',
            'floor_number' => 'sometimes|integer',
            'name' => 'nullable|string|max:100',
        ];
    }
}

