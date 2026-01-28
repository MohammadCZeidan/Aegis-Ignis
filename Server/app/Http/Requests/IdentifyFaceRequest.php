<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class IdentifyFaceRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
           'embedding' => 'required|array',
           'threshold' => 'nullable|numeric|min:0|max:1',
        ];
    }
}
