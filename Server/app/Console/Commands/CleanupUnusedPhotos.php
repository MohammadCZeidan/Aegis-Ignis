<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;

class CleanupUnusedPhotos extends Command
{
    
    protected $signature = 'photos:cleanup {--dry-run : Preview without deleting} {--force : Skip confirmation}';

   
    protected $description = 'Automatically cleanup unused employee photos not shown on website';

    
    public function handle()
    {
        $dryRun = $this->option('dry-run');
        $force = $this->option('force');

        $this->info('🧹 Automatic Photo Cleanup - Removing photos not shown on website');
        $this->newLine();

        if ($dryRun) {
            $this->warn('DRY RUN MODE - No files will be deleted');
            $this->newLine();
        }

        // Directories to check
        $directories = ['faces', 'employees', 'detections', 'alerts'];
        
        $stats = [
            'total_files' => 0,
            'used_files' => 0,
            'unused_files' => 0,
            'deleted_files' => 0,
            'errors' => 0,
            'space_freed' => 0
        ];

        // Get all photos referenced in the database (shown on website)
        $this->info('Scanning database for photos shown on website...');
        
        $usedPaths = [];
        
        // From employees table
        $employees = DB::table('employees')
            ->whereNotNull('face_photo_path')
            ->orWhereNotNull('photo_url')
            ->get(['face_photo_path', 'photo_url']);
        
        foreach ($employees as $employee) {
            if ($employee->face_photo_path) {
                $usedPaths[] = $employee->face_photo_path;
            }
            if ($employee->photo_url) {
                $path = str_replace([url('storage/'), '/storage/'], '', $employee->photo_url);
                $usedPaths[] = $path;
            }
        }
        
        // From detection_logs (recent detections shown on website) - if table exists
        try {
            $recentDetections = DB::table('detection_logs')
                ->where('created_at', '>=', now()->subDays(7))
                ->whereNotNull('detection_image_path')
                ->pluck('detection_image_path');
            
            foreach ($recentDetections as $path) {
                $usedPaths[] = $path;
            }
        } catch (\Exception $e) {
            // Table doesn't exist, skip
        }
        
        // From fire_alerts (shown on website) - if table exists
        try {
            $fireAlerts = DB::table('fire_alerts')
                ->where('created_at', '>=', now()->subDays(30))
                ->whereNotNull('image_path')
                ->pluck('image_path');
            
            foreach ($fireAlerts as $path) {
                $usedPaths[] = $path;
            }
        } catch (\Exception $e) {
            // Table doesn't exist, skip
        }
        
        $usedPaths = array_unique($usedPaths);
        $this->info("   Found " . count($usedPaths) . " photos currently shown on website");
        $this->newLine();

        $unusedFiles = [];

        // Scan each directory
        foreach ($directories as $directory) {
            $fullPath = storage_path("app/public/{$directory}");
            
            if (!is_dir($fullPath)) {
                continue;
            }
            
            $this->info("Scanning: storage/app/public/{$directory}");
            
            $files = scandir($fullPath);
            $filesInDir = 0;
            $unusedInDir = 0;
            
            foreach ($files as $file) {
                if ($file === '.' || $file === '..') {
                    continue;
                }
                
                $filePath = "{$fullPath}/{$file}";
                
                if (!is_file($filePath)) {
                    continue;
                }
                
                $filesInDir++;
                $stats['total_files']++;
                
                $relativePath = "{$directory}/{$file}";
                $isUsed = in_array($relativePath, $usedPaths);
                
                if ($isUsed) {
                    $stats['used_files']++;
                } else {
                    $stats['unused_files']++;
                    $unusedInDir++;
                    
                    $fileSize = filesize($filePath);
                    $unusedFiles[] = [
                        'path' => $filePath,
                        'relative_path' => $relativePath,
                        'size' => $fileSize,
                        'modified' => filemtime($filePath)
                    ];
                }
            }
            
            $this->line("   Files: {$filesInDir} | Unused: {$unusedInDir}");
        }
        
        $this->newLine();
        
        // Display results
        $this->info('═══════════════════════════════════');
        $this->info('   SCAN RESULTS');
        $this->info('═══════════════════════════════════');
        $this->line("Total files scanned:  {$stats['total_files']}");
        $this->line("Files shown on site:  {$stats['used_files']}");
        $this->warn("Unused files:         {$stats['unused_files']}");
        $this->newLine();

        if (count($unusedFiles) === 0) {
            $this->info('No unused files found! Storage is clean.');
            return 0;
        }

        // Calculate space
        foreach ($unusedFiles as $file) {
            $stats['space_freed'] += $file['size'];
        }
        
        $spaceMB = round($stats['space_freed'] / 1024 / 1024, 2);
        $this->warn("Space to be freed: {$spaceMB} MB from {$stats['unused_files']} files");
        $this->newLine();

        // Delete files
        if (!$dryRun) {
            if (!$force && !$this->confirm('Delete all unused photos?', true)) {
                $this->error('Operation cancelled.');
                return 1;
            }
            
            $this->info('Deleting unused files...');
            
            $progressBar = $this->output->createProgressBar(count($unusedFiles));
            $progressBar->start();
            
            foreach ($unusedFiles as $file) {
                try {
                    if (unlink($file['path'])) {
                        $stats['deleted_files']++;
                    } else {
                        $stats['errors']++;
                    }
                } catch (\Exception $e) {
                    $stats['errors']++;
                }
                $progressBar->advance();
            }
            
            $progressBar->finish();
            $this->newLine(2);
            
            $this->info('═══════════════════════════════════');
            $this->info('   CLEANUP COMPLETE');
            $this->info('═══════════════════════════════════');
            $this->line("Files deleted:        {$stats['deleted_files']}");
            $this->line("Errors:               {$stats['errors']}");
            $this->line("Space freed:          {$spaceMB} MB");
            $this->info('═══════════════════════════════════');
            $this->newLine();
            
            if ($stats['errors'] === 0) {
                $this->info('All unused photos successfully deleted!');
                
                // Log the cleanup
                \Log::info('Automatic photo cleanup completed', [
                    'deleted' => $stats['deleted_files'],
                    'space_freed_mb' => $spaceMB
                ]);
            } else {
                $this->warn("Completed with {$stats['errors']} errors.");
            }
        } else {
            $this->info('Dry run complete. No files deleted.');
            $this->line('   Run without --dry-run to delete files.');
        }

        return 0;
    }
}
