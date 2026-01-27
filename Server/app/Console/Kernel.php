<?php

namespace App\Console;

use Illuminate\Console\Scheduling\Schedule;
use Illuminate\Foundation\Console\Kernel as ConsoleKernel;

class Kernel extends ConsoleKernel
{
    protected $commands = [];

    protected function schedule(Schedule $schedule): void
    {
        // Automatic Photo Cleanup - Runs daily at 2 AM
        // Deletes any photos not shown on the website
        $schedule->command('photos:cleanup --force')
            ->dailyAt('02:00')
            ->withoutOverlapping()
            ->runInBackground()
            ->onSuccess(function () {
                \Log::info('Automatic photo cleanup completed successfully');
            })
            ->onFailure(function () {
                \Log::error('Automatic photo cleanup failed');
            });
        
        // Alert Cleanup - Runs hourly
        // Deletes alerts older than 1 day from database and filesystem
        $schedule->command('alerts:cleanup --days=1')
            ->hourly()
            ->withoutOverlapping()
            ->runInBackground()
            ->onSuccess(function () {
                \Log::info('Automatic alert cleanup completed successfully');
            })
            ->onFailure(function () {
                \Log::error('Automatic alert cleanup failed');
            });
        
        // Alert Cleanup - Also runs daily at 3 AM for thorough cleanup
        $schedule->command('alerts:cleanup --days=1')
            ->dailyAt('03:00')
            ->withoutOverlapping()
            ->runInBackground();
        
        // Legacy: Alert Images Cleanup (kept for backward compatibility)
        // Only deletes images, keeps database records
        $schedule->command('alerts:cleanup-images --days=1')
            ->dailyAt('03:30')
            ->withoutOverlapping()
            ->runInBackground();
    }

    protected function commands(): void
    {
        $this->load(__DIR__.'/Commands');

        require base_path('routes/console.php');
    }
}

