<?php

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Route;

/*
|--------------------------------------------------------------------------
| API Routes
|--------------------------------------------------------------------------
*/

// Health check endpoints
Route::get('/health', [App\Http\Controllers\Api\HealthController::class, 'index']);
Route::get('/ping', [App\Http\Controllers\Api\HealthController::class, 'ping']);

// Public employee registration endpoints (outside sanctum middleware)
Route::prefix('v1')->withoutMiddleware([\Laravel\Sanctum\Http\Middleware\EnsureFrontendRequestsAreStateful::class])->group(function () {
    Route::post('/employees/create-with-face', [App\Http\Controllers\Api\EmployeeController::class, 'createForFaceRegistration']);
    Route::get('/employees/next-id', [App\Http\Controllers\Api\EmployeeController::class, 'getNextEmployeeId']);
});

Route::prefix('v1')->group(function () {
    // Authentication routes - OUTSIDE auth:sanctum to avoid redirects
    Route::post('/auth/login/json', [App\Http\Controllers\Api\AuthController::class, 'login']);
    Route::post('/auth/register', [App\Http\Controllers\Api\AuthController::class, 'register']);
    
    // Authentication routes
    Route::prefix('auth')->group(function () {
        Route::middleware('auth:sanctum')->group(function () {
            Route::get('/me', [App\Http\Controllers\Api\AuthController::class, 'me']);
        });
    });
    
    // Public endpoints for building/camera data (for registration app)
    Route::get('/building/config', [App\Http\Controllers\Api\BuildingController::class, 'getConfig']); // MOVED TO PUBLIC
    Route::get('/floors', [App\Http\Controllers\Api\FloorController::class, 'index']);
    Route::get('/floors/{id}', [App\Http\Controllers\Api\FloorController::class, 'show']);
    Route::get('/cameras', [App\Http\Controllers\Api\CameraController::class, 'index']);
    Route::get('/cameras/{id}', [App\Http\Controllers\Api\CameraController::class, 'show']);
    Route::patch('/cameras/{id}/floor', [App\Http\Controllers\Api\CameraController::class, 'updateFloor']);
    Route::get('/employees', [App\Http\Controllers\Api\EmployeeControllerSimple::class, 'indexSimple']);
    
    // Public endpoints (for services)
    Route::post('/fire-detections/report', [App\Http\Controllers\Api\FireDetectionController::class, 'reportDetection']);
    
    // Alert endpoints (public for camera services)
    Route::post('/alerts/fire', [App\Http\Controllers\Api\AlertController::class, 'createFireAlert']);
    Route::get('/alerts', [App\Http\Controllers\Api\AlertController::class, 'index']);
    Route::get('/alerts/by-floor/{floorId}', [App\Http\Controllers\Api\AlertController::class, 'byFloor']);
    Route::post('/alerts/{id}/acknowledge', [App\Http\Controllers\Api\AlertController::class, 'acknowledge']);
    
    // Presence tracking endpoints (public for camera services)
    Route::post('/presence/entry', [App\Http\Controllers\Api\PresenceController::class, 'logEntry']);
    Route::post('/presence/exit', [App\Http\Controllers\Api\PresenceController::class, 'logExit']);
    Route::get('/presence/current', [App\Http\Controllers\Api\PresenceController::class, 'getCurrentPresence']);
    Route::get('/presence/people', [App\Http\Controllers\Api\PresenceController::class, 'getAllPeopleInBuilding']);
    
    // Face recognition service endpoints (public for microservice)
    Route::post('/employees/{id}/register-face', [App\Http\Controllers\Api\EmployeeController::class, 'registerFaceEmbedding']);
    Route::get('/employees/registered-faces', [App\Http\Controllers\Api\EmployeeController::class, 'getRegisteredFaces']);
    Route::post('/employees/check-face-duplicate', [App\Http\Controllers\Api\EmployeeController::class, 'checkFaceDuplicate']);
    Route::post('/employees/identify-face', [App\Http\Controllers\Api\EmployeeController::class, 'identifyFace']);
    
    // Presence tracking (public for microservice)
    Route::post('/presence/log', [App\Http\Controllers\Api\PresenceController::class, 'logPresence']);
    Route::post('/presence/update-floor', [App\Http\Controllers\Api\PresenceController::class, 'updateFloorPresence']);
    Route::get('/presence/floor-live/{floorId}', [App\Http\Controllers\Api\PresenceController::class, 'getFloorPresence']);
    
    // Emergency alerts (public for microservice and frontend)
    Route::post('/emergency/fire-alert', [App\Http\Controllers\Api\EmergencyController::class, 'createFireAlert']);
    Route::get('/emergency/alerts/active', [App\Http\Controllers\Api\EmergencyController::class, 'getActiveAlerts']);
    Route::get('/emergency/alerts/history', [App\Http\Controllers\Api\EmergencyController::class, 'getAlertHistory']);
    Route::post('/emergency/alerts/{id}/acknowledge', [App\Http\Controllers\Api\EmergencyController::class, 'acknowledgeAlert']);
    Route::post('/emergency/alerts/{id}/resolve', [App\Http\Controllers\Api\EmergencyController::class, 'resolveAlert']);

    // Protected routes
    Route::middleware('auth:sanctum')->group(function () {
        // Employees
        Route::prefix('employees')->group(function () {
            // Route::get('/', [App\Http\Controllers\Api\EmployeeController::class, 'index']); // Moved to public section above
            Route::get('/by-floor/{floorId}', [App\Http\Controllers\Api\EmployeeController::class, 'byFloor']);
            Route::post('/register-face', [App\Http\Controllers\Api\EmployeeController::class, 'registerFace']);
            Route::delete('/{id}', [App\Http\Controllers\Api\EmployeeController::class, 'destroy']);
        });

        // Protected floor management (create/update/delete)
        Route::prefix('floors')->group(function () {
            Route::post('/', [App\Http\Controllers\Api\FloorController::class, 'store']);
            Route::put('/{id}', [App\Http\Controllers\Api\FloorController::class, 'update']);
            Route::delete('/{id}', [App\Http\Controllers\Api\FloorController::class, 'destroy']);
        });

        // Protected camera management (create/update/delete)
        Route::prefix('cameras')->group(function () {
            Route::post('/', [App\Http\Controllers\Api\CameraController::class, 'store']);
            Route::put('/{id}', [App\Http\Controllers\Api\CameraController::class, 'update']);
            Route::delete('/{id}', [App\Http\Controllers\Api\CameraController::class, 'destroy']);
        });
        
        // Fire Detection (protected endpoints)
        Route::prefix('fire-detections')->group(function () {
            Route::get('/', [App\Http\Controllers\Api\FireDetectionController::class, 'index']);
            Route::get('/{id}', [App\Http\Controllers\Api\FireDetectionController::class, 'show']);
            Route::post('/{id}/resolve', [App\Http\Controllers\Api\FireDetectionController::class, 'resolve']);
        });

        // Occupancy
        Route::prefix('occupancy')->group(function () {
            Route::get('/summary', [App\Http\Controllers\Api\OccupancyController::class, 'summary']);
            Route::get('/floors/{floorId}', [App\Http\Controllers\Api\OccupancyController::class, 'byFloor']);
        });
        
        // Presence tracking
        Route::prefix('presence')->group(function () {
            Route::get('/people', [App\Http\Controllers\Api\PresenceController::class, 'getAllPeopleInBuilding']);
            Route::get('/floor/{floorId}', [App\Http\Controllers\Api\PresenceController::class, 'getPeopleByFloor']);
            Route::get('/employee/{id}', [App\Http\Controllers\Api\PresenceController::class, 'getEmployeeDetails']);
            Route::get('/stats', [App\Http\Controllers\Api\PresenceController::class, 'getOccupancyStats']);
        });
        
        // Emergency management
        Route::prefix('emergency')->group(function () {
            Route::get('/alerts/active', [App\Http\Controllers\Api\EmergencyController::class, 'getActiveAlerts']);
            Route::get('/alerts/history', [App\Http\Controllers\Api\EmergencyController::class, 'getAlertHistory']);
            Route::post('/alerts/{id}/acknowledge', [App\Http\Controllers\Api\EmergencyController::class, 'acknowledgeAlert']);
            Route::post('/alerts/{id}/resolve', [App\Http\Controllers\Api\EmergencyController::class, 'resolveAlert']);
        });
        
        // Building Configuration & Management (protected updates only)
        Route::prefix('building')->group(function () {
            Route::put('/config', [App\Http\Controllers\Api\BuildingController::class, 'updateConfig']);
            Route::delete('/alerts/all', [App\Http\Controllers\Api\BuildingController::class, 'deleteAllAlerts']);
        });
    });
});

// Simplified auth routes at root level for standalone auth pages
Route::post('/login', [App\Http\Controllers\Api\AuthController::class, 'login']);
Route::post('/register', [App\Http\Controllers\Api\AuthController::class, 'register']);
Route::middleware('auth:sanctum')->get('/user', [App\Http\Controllers\Api\AuthController::class, 'me']);
