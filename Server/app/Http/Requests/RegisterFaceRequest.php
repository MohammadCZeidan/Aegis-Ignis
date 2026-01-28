<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class RegisterFaceRequest extends FormRequest
{
   
    public function authorize(): bool
    {
        return $this->user()->role === 'admin';
    }

    
    public function rules(): array
    {
        return [
            'name' => 'required|string|max:255',
            'email' => 'nullable|email|unique:employees,email',            'password' => 'required|string|min:6',            'floor_id' => 'nullable|exists:floors,id',
            'photo' => 'required|file|mimes:jpg,jpeg,png|max:10240', // 10MB max
        ];
    }

    
    public function messages(): array
    {
        return [
            'photo.required' => 'A photo is required to register an employee.',
            'photo.image' => 'The uploaded file must be an image.',
            'photo.max' => 'The photo size must not exceed 10MB.',
        ];
    }
}

