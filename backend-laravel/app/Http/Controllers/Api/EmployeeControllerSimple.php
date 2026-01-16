<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use App\Models\Employee;

class EmployeeControllerSimple extends Controller
{
    /**
     * List all employees
     */
    public function indexSimple()
    {
        $employees = Employee::all();
        
        return response()->json([
            'employees' => $employees,
            'total' => $employees->count(),
        ]);
    }
}
