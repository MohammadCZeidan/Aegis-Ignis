<?php

namespace App\Http\Requests;

use Illuminate\Foundation\Http\FormRequest;

class CreateEmployeeRequest extends FormRequest
{
    public function authorize(): bool
    {
        return true;
    }

    public function rules(): array
    {
        return [
           'name' => 'required|string|max:255',
           'employee_number' => 'required|string|unique:employees,employee_number',
           'department' => 'required|string|max:255',
           'email' => 'required|email|unique:employees,email',
           'password' => 'required|string|min:6',
           'role' => 'nullable|string|in:admin,employee'
        ];
    }
}
