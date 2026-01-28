<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;

class ServiceStatus extends Command
{
   
    protected $signature = 'services:status';

   
    protected $description = 'Check status of all microservices';

     
    public function handle()
    {
        $this->info('AEGIS-IGNIS Service Status');
        $this->newLine();

        // Check Laravel
        $this->checkService('Laravel Backend', 'http://localhost:8000/ping', 8000);

        // Check Face Service
        $this->checkService('Face Recognition Service', 'http://localhost:8001/health', 8001);

        // Check Fire Service
        $this->checkService('Fire Detection Service', 'http://localhost:8002/health', 8002);

        $this->newLine();
    }

    protected function checkService(string $name, string $url, int $port): void
    {
        $this->line("Checking {$name}...");

        try {
            $response = Http::timeout(3)->get($url);

            if ($response->successful()) {
                $data = $response->json();
                $status = $data['status'] ?? 'unknown';
                
                $this->info("  ✓ {$name} is running");
                $this->line("    Port: {$port}");
                $this->line("    Status: {$status}");
                
                if (isset($data['model_loaded'])) {
                    $this->line("    Model: " . ($data['model_loaded'] ? 'Loaded' : 'Not loaded'));
                }
            } else {
                $this->warn("  [WARNING] {$name} responded with status {$response->status()}");
            }
        } catch (\Exception $e) {
            $this->error("  ✗ {$name} is not running or unreachable");
            $this->line("    Error: " . $e->getMessage());
        }

        $this->newLine();
    }
}

