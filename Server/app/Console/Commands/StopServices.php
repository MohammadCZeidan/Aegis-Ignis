<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Process;

class StopServices extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'services:stop 
                            {--face : Stop face recognition service}
                            {--fire : Stop fire detection service}
                            {--all : Stop all services}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Stop Python microservices';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $stopAll = $this->option('all');
        $stopFace = $this->option('face') || $stopAll;
        $stopFire = $this->option('fire') || $stopAll;

        $this->info('🛑 Stopping AEGIS-IGNIS Services...');
        $this->newLine();

        if ($stopFace) {
            $this->stopService(8001, 'Face Recognition Service');
        }

        if ($stopFire) {
            $this->stopService(8002, 'Fire Detection Service');
        }

        if (!$stopFace && !$stopFire) {
            $this->warn('No services selected. Use --face, --fire, or --all');
        }

        $this->newLine();
        $this->info('Services stopped!');
    }

    protected function stopService(int $port, string $serviceName): void
    {
        $this->info("Stopping {$serviceName} (port {$port})...");

        if (PHP_OS_FAMILY === 'Windows') {
            // Windows: Find and kill process using the port
            $result = Process::run("netstat -ano | findstr :{$port}");
            if ($result->successful() && !empty($result->output())) {
                $lines = explode("\n", trim($result->output()));
                foreach ($lines as $line) {
                    if (preg_match('/\s+(\d+)$/', $line, $matches)) {
                        $pid = $matches[1];
                        Process::run("taskkill /F /PID {$pid}");
                        $this->info("✓ Stopped process {$pid}");
                    }
                }
            } else {
                $this->warn("No process found on port {$port}");
            }
        } else {
            // Linux/Mac: Find and kill process using the port
            $result = Process::run("lsof -ti:{$port}");
            if ($result->successful() && !empty($result->output())) {
                $pids = explode("\n", trim($result->output()));
                foreach ($pids as $pid) {
                    Process::run("kill {$pid}");
                    $this->info("✓ Stopped process {$pid}");
                }
            } else {
                $this->warn("No process found on port {$port}");
            }
        }
    }
}

