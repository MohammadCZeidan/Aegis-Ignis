<?php

require __DIR__ . '/vendor/autoload.php';

$app = require_once __DIR__ . '/bootstrap/app.php';
$kernel = $app->make(Illuminate\Contracts\Console\Kernel::class);
$kernel->bootstrap();

echo "===== CLEANING FAKE FIRE ALERTS =====\n\n";

// Delete alerts without screenshots (definitely fake)
$deletedNoScreenshot = \App\Models\Alert::whereNull('screenshot_path')->delete();
echo "✅ Deleted $deletedNoScreenshot alerts without screenshots\n";

// Delete old alerts with low confidence (<60%)
$deletedLowConfidence = \App\Models\Alert::where('confidence', '<', 60)->delete();
echo "✅ Deleted $deletedLowConfidence alerts with confidence <60%\n";

// Delete alerts older than 1 day (cleanup old data)
$oneDayAgo = now()->subDay();
$deletedOld = \App\Models\Alert::where('created_at', '<', $oneDayAgo)->delete();
echo "✅ Deleted $deletedOld alerts older than 24 hours\n";

// Show remaining
$remaining = \App\Models\Alert::count();
echo "\n📊 Remaining alerts: $remaining\n";

if ($remaining > 0) {
    echo "\nRecent HIGH confidence alerts:\n";
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n";
    
    $recent = \App\Models\Alert::where('confidence', '>=', 60)
        ->orderBy('created_at', 'desc')
        ->limit(5)
        ->get(['id', 'confidence', 'detected_at', 'screenshot_path']);
    
    foreach ($recent as $alert) {
        $hasScreenshot = $alert->screenshot_path ? '✅' : '❌';
        echo "#{$alert->id} - {$alert->confidence}% - {$alert->detected_at} {$hasScreenshot}\n";
    }
}

echo "\n✅ CLEANUP COMPLETE!\n";
