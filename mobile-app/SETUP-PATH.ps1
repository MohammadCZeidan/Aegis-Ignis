# PowerShell Script to Add Android SDK and Java to PATH
# Run this script as Administrator

Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Setting up Android Development Environment PATH" -ForegroundColor Cyan
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if running as Administrator
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "[WARNING] This script requires Administrator privileges!" -ForegroundColor Yellow
    Write-Host "Right-click PowerShell and select 'Run as Administrator'" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Or manually add these paths to System PATH:" -ForegroundColor Yellow
    Write-Host "  1. Press Win + X -> System" -ForegroundColor Yellow
    Write-Host "  2. Advanced system settings -> Environment Variables" -ForegroundColor Yellow
    Write-Host "  3. Add the paths shown below" -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 1
}

# Find paths
$sdkPath = "$env:LOCALAPPDATA\Android\Sdk"
$javaPath = "C:\Program Files\Android\Android Studio\jbr\bin"
$platformTools = "$sdkPath\platform-tools"
$emulator = "$sdkPath\emulator"

Write-Host "[1] Checking Android SDK..." -ForegroundColor Yellow
if (Test-Path $sdkPath) {
    Write-Host "    [OK] Android SDK found: $sdkPath" -ForegroundColor Green
} else {
    Write-Host "    [ERROR] Android SDK not found at: $sdkPath" -ForegroundColor Red
    Write-Host "    Please install Android Studio first!" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "[2] Checking Java..." -ForegroundColor Yellow
if (Test-Path $javaPath) {
    Write-Host "    [OK] Java found: $javaPath" -ForegroundColor Green
} else {
    Write-Host "    [WARNING] Java not found at: $javaPath" -ForegroundColor Yellow
    Write-Host "    Trying alternative location..." -ForegroundColor Yellow
    $javaPath = "C:\Program Files\Android\Android Studio\jre\bin"
    if (Test-Path $javaPath) {
        Write-Host "    [OK] Java found at alternative location" -ForegroundColor Green
    } else {
        Write-Host "    [ERROR] Java not found. Please check Android Studio installation." -ForegroundColor Red
        pause
        exit 1
    }
}

# Get current PATH
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")

# Paths to add
$pathsToAdd = @(
    $platformTools,
    $emulator,
    $javaPath
)

Write-Host "[3] Adding paths to System PATH..." -ForegroundColor Yellow

$updated = $false
foreach ($path in $pathsToAdd) {
    if ($currentPath -notlike "*$path*") {
        Write-Host "    Adding: $path" -ForegroundColor Cyan
        $currentPath = "$currentPath;$path"
        $updated = $true
    } else {
        Write-Host "    [SKIP] Already in PATH: $path" -ForegroundColor Gray
    }
}

if ($updated) {
    [Environment]::SetEnvironmentVariable("Path", $currentPath, "Machine")
    Write-Host "    [OK] PATH updated successfully!" -ForegroundColor Green
} else {
    Write-Host "    [OK] All paths already in PATH!" -ForegroundColor Green
}

# Set JAVA_HOME
Write-Host "[4] Setting JAVA_HOME..." -ForegroundColor Yellow
$javaHome = Split-Path $javaPath -Parent
$currentJavaHome = [Environment]::GetEnvironmentVariable("JAVA_HOME", "Machine")

if ($currentJavaHome -ne $javaHome) {
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome, "Machine")
    Write-Host "    [OK] JAVA_HOME set to: $javaHome" -ForegroundColor Green
} else {
    Write-Host "    [OK] JAVA_HOME already set correctly" -ForegroundColor Green
}

Write-Host ""
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host "  Setup Complete!" -ForegroundColor Green
Write-Host "================================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT: Close and reopen ALL terminal windows for changes to take effect!" -ForegroundColor Yellow
Write-Host ""
Write-Host "After restarting terminal, test with:" -ForegroundColor Cyan
Write-Host "  adb devices" -ForegroundColor White
Write-Host "  java -version" -ForegroundColor White
Write-Host "  emulator -list-avds" -ForegroundColor White
Write-Host ""
pause
