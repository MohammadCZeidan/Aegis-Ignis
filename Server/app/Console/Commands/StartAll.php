<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;

class StartAll extends Command
{
   
    protected $signature = 'start:all';

       protected $description = 'Start Laravel backend and all microservices (one command to rule them all!)';

    
    public function handle()
    {
        $this->info('AEGIS-IGNIS - Unified Laravel Backend');
        $this->newLine();
        $this->info('This is your ONE backend - everything is managed through Laravel!');
        $this->newLine();
        $this->info('To start everything:');
        $this->newLine();
        $this->line('1. Start Laravel server:');
        $this->line('   php artisan serve');
        $this->newLine();
        $this->line('2. In another terminal, start Python services:');
        $this->line('   php artisan services:start --all');
        $this->newLine();
        $this->info('Or use the unified startup script:');
        $this->line('   .\start-all.ps1  (Windows)');
        $this->line('   ./start-all.sh   (Linux/Mac)');
        $this->newLine();
        $this->info('Check service status:');
        $this->line('   php artisan services:status');
    }
}

