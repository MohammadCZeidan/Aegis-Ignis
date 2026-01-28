<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class StoreFloorRequest extends FormRequest
{
    
    public function authorize(): bool
    {
        return $this->user()->role === 'admin';
    }

    
    public function rules(): array
    {
        return [
            'building_id' => 'required|exists:buildings,id',
            'floor_number' => 'required|integer',
            'name' => 'nullable|string|max:100',
        ];
    }
}

