<?php

namespace App\Services;

use App\Models\Alert;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Log;

class AlertCleanupService
{
    public function cleanupImages(int $days = 1, bool $deleteAll = false): array
    {
        try {
            $query = Alert::query();
            
            if (!$deleteAll) {
                $query->where('created_at', '<=', now()->subDays($days));
            }
            
            $alerts = $query->get();
            $deletedCount = 0;
            $filesDeleted = 0;
            
            foreach ($alerts as $alert) {
                // Delete image file if exists
                if ($alert->image) {
                    $imagePath = 'public/alerts/' . basename($alert->image);
                    
                    if (Storage::exists($imagePath)) {
                        Storage::delete($imagePath);
                        $filesDeleted++;
                    }
                    
                    $alert->image = null;
                    $alert->save();
                    $deletedCount++;
                }
                
                // Also check screenshot_path
                if ($alert->screenshot_path) {
                    $screenshotPath = 'public/alerts/' . basename($alert->screenshot_path);
                    
                    if (Storage::exists($screenshotPath)) {
                        Storage::delete($screenshotPath);
                        $filesDeleted++;
                    }
                    
                    $alert->screenshot_path = null;
                    $alert->save();
                    $deletedCount++;
                }
            }
            
            // Clean up any orphaned files
            $allFiles = Storage::files('public/alerts');
            foreach ($allFiles as $file) {
                if (!$deleteAll) {
                    $lastModified = Storage::lastModified($file);
                    if ($lastModified <= now()->subDays($days)->timestamp) {
                        Storage::delete($file);
                        $filesDeleted++;
                    }
                } else {
                    Storage::delete($file);
                    $filesDeleted++;
                }
            }
            
            Log::info('Alert images cleanup completed', [
                'alerts_updated' => $deletedCount,
                'files_deleted' => $filesDeleted,
                'days' => $deleteAll ? 'all' : $days
            ]);
            
            return [
                'success' => true,
                'alerts_updated' => $deletedCount,
                'files_deleted' => $filesDeleted,
                'message' => "Cleanup completed: {$deletedCount} alerts updated, {$filesDeleted} files deleted"
            ];
            
        } catch (\Exception $e) {
            Log::error('Alert images cleanup failed', [
                'error' => $e->getMessage()
            ]);
            
            return [
                'success' => false,
                'error' => 'Cleanup failed: ' . $e->getMessage()
            ];
        }
    }
}
