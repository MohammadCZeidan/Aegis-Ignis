<?php

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\Process;

class StartServices extends Command
{
    /**
     * The name and signature of the console command.
     *
     * @var string
     */
    protected $signature = 'services:start 
                            {--face : Start face recognition service}
                            {--fire : Start fire detection service}
                            {--all : Start all services}';

    /**
     * The console command description.
     *
     * @var string
     */
    protected $description = 'Start Python microservices (face recognition, fire detection)';

    /**
     * Execute the console command.
     */
    public function handle()
    {
        $projectRoot = base_path('..');
        $startAll = $this->option('all');
        $startFace = $this->option('face') || $startAll;
        $startFire = $this->option('fire') || $startAll;

        $this->info('🚀 Starting AEGIS-IGNIS Services...');
        $this->newLine();

        if ($startFace) {
            $this->startFaceService($projectRoot);
        }

        if ($startFire) {
            $this->startFireService($projectRoot);
        }

        if (!$startFace && !$startFire) {
            $this->warn('No services selected. Use --face, --fire, or --all');
            $this->info('Example: php artisan services:start --all');
        }

        $this->newLine();
        $this->info('✅ Services started!');
        $this->info('   • Laravel API: http://localhost:8000');
        if ($startFace) {
            $this->info('   • Face Service: http://localhost:8001');
        }
        if ($startFire) {
            $this->info('   • Fire Service: http://localhost:8002');
        }
    }

    protected function startFaceService(string $projectRoot): void
    {
        $this->info('Starting Face Recognition Service...');
        
        $faceServicePath = $projectRoot . DIRECTORY_SEPARATOR . 'python-face-service';
        
        if (!is_dir($faceServicePath)) {
            $this->error("Face service directory not found: {$faceServicePath}");
            return;
        }

        // Check if Python is available
        $pythonCmd = $this->findPython();
        if (!$pythonCmd) {
            $this->error('Python not found. Please install Python 3.8+');
            return;
        }

        // Check if venv exists, create if not
        $venvPath = $faceServicePath . DIRECTORY_SEPARATOR . 'venv';
        if (!is_dir($venvPath)) {
            $this->info('Creating Python virtual environment...');
            Process::run("{$pythonCmd} -m venv {$venvPath}")->throw();
        }

        // Install dependencies
        $pipPath = $venvPath . DIRECTORY_SEPARATOR . 'Scripts' . DIRECTORY_SEPARATOR . 'pip.exe';
        if (PHP_OS_FAMILY !== 'Windows') {
            $pipPath = $venvPath . DIRECTORY_SEPARATOR . 'bin' . DIRECTORY_SEPARATOR . 'pip';
        }

        if (file_exists($pipPath)) {
            $this->info('Installing Python dependencies...');
            Process::path($faceServicePath)->run("{$pipPath} install -q -r requirements.txt");
        }

        // Start service
        $pythonPath = $venvPath . DIRECTORY_SEPARATOR . 'Scripts' . DIRECTORY_SEPARATOR . 'python.exe';
        if (PHP_OS_FAMILY !== 'Windows') {
            $pythonPath = $venvPath . DIRECTORY_SEPARATOR . 'bin' . DIRECTORY_SEPARATOR . 'python';
        }

        $this->info('Starting Face Service on port 8001...');
        
        if (PHP_OS_FAMILY === 'Windows') {
            Process::path($faceServicePath)
                ->start("start \"Face Service\" cmd /k \"{$pythonPath} main.py\"");
        } else {
            Process::path($faceServicePath)
                ->start("nohup {$pythonPath} main.py > /dev/null 2>&1 &");
        }

        $this->info('✓ Face Recognition Service started');
    }

    protected function startFireService(string $projectRoot): void
    {
        $this->info('Starting Fire Detection Service...');
        
        $fireServicePath = $projectRoot . DIRECTORY_SEPARATOR . 'fire-detection-service';
        
        if (!is_dir($fireServicePath)) {
            $this->error("Fire service directory not found: {$fireServicePath}");
            return;
        }

        // Check if Python is available
        $pythonCmd = $this->findPython();
        if (!$pythonCmd) {
            $this->error('Python not found. Please install Python 3.8+');
            return;
        }

        // Install dependencies if needed
        $this->info('Installing Python dependencies...');
        Process::path($fireServicePath)->run("{$pythonCmd} -m pip install -q -r requirements.txt");

        // Start service
        $this->info('Starting Fire Service on port 8002...');
        
        if (PHP_OS_FAMILY === 'Windows') {
            Process::path($fireServicePath)
                ->start("start \"Fire Service\" cmd /k \"{$pythonCmd} main.py\"");
        } else {
            Process::path($fireServicePath)
                ->start("nohup {$pythonCmd} main.py > /dev/null 2>&1 &");
        }

        $this->info('✓ Fire Detection Service started');
    }

    protected function findPython(): ?string
    {
        $commands = ['python3', 'python'];
        
        foreach ($commands as $cmd) {
            $result = Process::run("{$cmd} --version");
            if ($result->successful()) {
                return $cmd;
            }
        }
        
        return null;
    }
}

