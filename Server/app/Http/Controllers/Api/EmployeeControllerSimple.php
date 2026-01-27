<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Employee;
use Illuminate\Support\Facades\Storage;

class EmployeeControllerSimple extends Controller
{
    /**
     * List all employees with photo URLs
     */
    public function indexSimple()
    {
        $employees = Employee::all()->map(function ($employee) {
            return [
                'id' => $employee->id,
                'name' => $employee->name,
                'employee_number' => $employee->employee_number,
                'department' => $employee->department,
                'email' => $employee->email,
                'role' => $employee->role,
                'status' => $employee->status,
                'photo_url' => $employee->photo_url, // URL to photo
                'face_photo_path' => $employee->face_photo_path,
                'last_seen_at' => $employee->last_seen_at,
                'created_at' => $employee->created_at,
                'updated_at' => $employee->updated_at,
            ];
        });
        
        return response()->json([
            'employees' => $employees,
            'total' => $employees->count(),
        ]);
    }

    /**
     * Get employee photo as base64
     */
    public function getEmployeePhoto($id)
    {
        $employee = Employee::findOrFail($id);
        
        if (!$employee->face_photo_path) {
            return response()->json([
                'error' => 'No photo found for this employee'
            ], 404);
        }

        // Check if file exists
        if (!Storage::disk('public')->exists($employee->face_photo_path)) {
            return response()->json([
                'error' => 'Photo file not found'
            ], 404);
        }

        // Get the file content
        $fileContent = Storage::disk('public')->get($employee->face_photo_path);
        $base64 = base64_encode($fileContent);
        
        // Get mime type
        $mimeType = Storage::disk('public')->mimeType($employee->face_photo_path);
        
        return response()->json([
            'employee_id' => $employee->id,
            'name' => $employee->name,
            'photo_base64' => $base64,
            'mime_type' => $mimeType,
            'data_url' => "data:{$mimeType};base64,{$base64}", // Ready to use in <img> tag
        ]);
    }
}
