<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\Alert;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Log;

class CleanupAlertImages extends Command
{
    protected $signature = 'alerts:cleanup-images {--days=1 : Number of days old to delete} {--all : Delete all alert images}';
    protected $description = 'Delete alert images from database and filesystem';

    public function handle()
    {
        $deleteAll = $this->option('all');
        $days = (int) $this->option('days'); 
        $this->info('Starting alert images cleanup...');
                try {
            $query = Alert::query();
            
            if (!$deleteAll) {
                $query->where('created_at', '<=', now()->subDays($days));
                $this->info("Cleaning up alerts older than {$days} days");
            } else {
                $this->info("Cleaning up ALL alert images");
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
                        $this->line("Deleted file: {$imagePath}");
                    }
                    
                    // Clear image from database
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
                        $this->line("Deleted file: {$screenshotPath}");
                    }
                    
                    // Clear screenshot_path from database
                    $alert->screenshot_path = null;
                    $alert->save();
                    $deletedCount++;
                }
            }
            
            // Clean up any orphaned files in the alerts directory
            $allFiles = Storage::files('public/alerts');
            foreach ($allFiles as $file) {
                if (!$deleteAll) {
                    $lastModified = Storage::lastModified($file);
                    if ($lastModified <= now()->subDays($days)->timestamp) {
                        Storage::delete($file);
                        $filesDeleted++;
                        $this->line("Deleted orphaned file: {$file}");
                    }
                } else {
                    Storage::delete($file);
                    $filesDeleted++;
                    $this->line("Deleted file: {$file}");
                }
            }
            
            Log::info('Alert images cleanup completed', [
                'alerts_updated' => $deletedCount,
                'files_deleted' => $filesDeleted,
                'days' => $deleteAll ? 'all' : $days
            ]);
            
            $this->info("Cleanup completed!");
            $this->info("   - Updated {$deletedCount} alerts");
            $this->info("   - Deleted {$filesDeleted} files");
            
            return 0;
            
        } catch (\Exception $e) {
            Log::error('Alert images cleanup failed', [
                'error' => $e->getMessage()
            ]);
            
            $this->error("Cleanup failed: {$e->getMessage()}");
            return 1;
        }
    }
}
