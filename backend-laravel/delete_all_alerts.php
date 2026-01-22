<?php

require __DIR__ . '/vendor/autoload.php';

$app = require_once __DIR__ . '/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

echo "===== DELETE ALL FAKE FIRE ALERTS =====\n\n";

// Disable foreign key checks temporarily
\DB::statement('SET FOREIGN_KEY_CHECKS=0;');

$alertCount = \App\Models\Alert::count();
$fireEventCount = \App\Models\FireEvent::count();

echo "Before:\n";
echo "  Alerts: $alertCount\n";
echo "  Fire Events: $fireEventCount\n\n";

// Delete all
\App\Models\Alert::truncate();
\App\Models\FireEvent::truncate();

echo "After:\n";
echo "  Alerts: " . \App\Models\Alert::count() . "\n";
echo "  Fire Events: " . \App\Models\FireEvent::count() . "\n\n";

// Re-enable foreign key checks
\DB::statement('SET FOREIGN_KEY_CHECKS=1;');

echo "[OK] DELETED ALL $alertCount ALERTS!\n\n";

// Check camera configuration
echo "===== CAMERA CONFIGURATION =====\n\n";
$camera = \App\Models\Camera::find(1);
if ($camera) {
    echo "Camera 1: {$camera->name}\n";
    echo "Floor ID: {$camera->floor_id}\n";
    
    $floor = \App\Models\Floor::find($camera->floor_id);
    if ($floor) {
        echo "Floor Name: {$floor->name}\n";
    } else {
        echo "Floor NOT FOUND in database!\n";
        echo "Available floors:\n";
        foreach (\App\Models\Floor::all() as $f) {
            echo "  - Floor {$f->id}: {$f->name}\n";
        }
    }
} else {
    echo "Camera 1 NOT FOUND!\n";
}

echo "\n[OK] DONE!\n";
