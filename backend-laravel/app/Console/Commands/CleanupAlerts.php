<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use App\Models\Alert;
use Illuminate\Support\Facades\Storage;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\DB;

class CleanupAlerts extends Command
{
    protected $signature = 'alerts:cleanup 
                            {--days=1 : Number of days old to delete} 
                            {--all : Delete all alerts}
                            {--images-only : Only delete images, keep database records}';
    
    protected $description = 'Delete alerts from database and filesystem';

    public function handle()
    {
        $deleteAll = $this->option('all');
        $days = (int) $this->option('days');
        $imagesOnly = $this->option('images-only');
        
        $this->info('Starting alert cleanup...');
        
        try {
            $query = Alert::query();
            
            if (!$deleteAll) {
                $query->where('created_at', '<=', now()->subDays($days));
                $this->info("Cleaning up alerts older than {$days} days");
            } else {
                $this->info("Cleaning up ALL alerts");
            }
            
            $alerts = $query->get();
            $recordsDeleted = 0;
            $filesDeleted = 0;
            
            foreach ($alerts as $alert) {
                // Delete image files
                if ($alert->image) {
                    $imagePath = 'public/alerts/' . basename($alert->image);
                    if (Storage::exists($imagePath)) {
                        Storage::delete($imagePath);
                        $filesDeleted++;
                        $this->line("Deleted file: {$imagePath}");
                    }
                }
                
                if ($alert->screenshot_path) {
                    $screenshotPath = 'public/alerts/' . basename($alert->screenshot_path);
                    if (Storage::exists($screenshotPath)) {
                        Storage::delete($screenshotPath);
                        $filesDeleted++;
                        $this->line("Deleted file: {$screenshotPath}");
                    }
                }
                
                // Delete database record (unless images-only)
                if (!$imagesOnly) {
                    $alert->delete();
                    $recordsDeleted++;
                } else {
                    // Just clear image paths
                    $alert->image = null;
                    $alert->screenshot_path = null;
                    $alert->save();
                }
            }
            
            // Clean up orphaned files in alerts directory
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
            
            // Also clean up fire_alerts table if it exists
            if (!$imagesOnly) {
                $fireAlertsQuery = DB::table('fire_alerts');
                if (!$deleteAll) {
                    $fireAlertsQuery->where('created_at', '<=', now()->subDays($days));
                }
                $fireAlertsDeleted = $fireAlertsQuery->delete();
                $recordsDeleted += $fireAlertsDeleted;
            }
            
            Log::info('Alert cleanup completed', [
                'records_deleted' => $recordsDeleted,
                'files_deleted' => $filesDeleted,
                'days' => $deleteAll ? 'all' : $days,
                'images_only' => $imagesOnly
            ]);
            
            $this->info("Cleanup completed!");
            if (!$imagesOnly) {
                $this->info("   - Deleted {$recordsDeleted} alert records");
            }
            $this->info("   - Deleted {$filesDeleted} files");
            
            return 0;
            
        } catch (\Exception $e) {
            Log::error('Alert cleanup failed', [
                'error' => $e->getMessage(),
                'trace' => $e->getTraceAsString()
            ]);
            
            $this->error("Cleanup failed: {$e->getMessage()}");
            return 1;
        }
    }
}
