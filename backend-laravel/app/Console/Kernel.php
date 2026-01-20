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
        
        // Alert Images Cleanup - Runs daily at 3 AM
        // Deletes alert images older than 1 day from database and filesystem
        $schedule->command('alerts:cleanup-images --days=1')
            ->dailyAt('03:00')
            ->withoutOverlapping()
            ->runInBackground()
            ->onSuccess(function () {
                \Log::info('Automatic alert images cleanup completed successfully');
            })
            ->onFailure(function () {
                \Log::error('Automatic alert images cleanup failed');
            });
    }

    protected function commands(): void
    {
        $this->load(__DIR__.'/Commands');

        require base_path('routes/console.php');
    }
}

