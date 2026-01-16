<?php

use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    return response()->json([
        'message' => 'Aegis-Ignis API',
        'version' => '1.0.0',
        'docs' => '/api/v1'
    ]);
});

