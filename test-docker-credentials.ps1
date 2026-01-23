# Test Docker Hub Credentials
# This script tests if your Docker Hub username and token work correctly

Write-Host "=== Docker Hub Credential Test ===" -ForegroundColor Cyan
Write-Host ""

# Prompt for username
$username = Read-Host "Enter your Docker Hub username (or press Enter to use 'mhmdczaidan')"
if ([string]::IsNullOrWhiteSpace($username)) {
    $username = "mhmdczaidan"
}

# Prompt for token (hidden input)
Write-Host "Enter your Docker Hub Personal Access Token (input will be hidden):" -ForegroundColor Yellow
$secureToken = Read-Host -AsSecureString
$token = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secureToken)
)

Write-Host ""
Write-Host "Testing Docker login..." -ForegroundColor Yellow

# Test login
$loginResult = echo $token | docker login -u $username --password-stdin 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ SUCCESS! Docker Hub login successful!" -ForegroundColor Green
    Write-Host "Your credentials are valid." -ForegroundColor Green
    Write-Host ""
    
    # Test pulling an image (optional)
    Write-Host "Testing image pull..." -ForegroundColor Yellow
    docker pull hello-world 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Image pull successful!" -ForegroundColor Green
    }
    
    # Logout
    docker logout 2>&1 | Out-Null
    Write-Host ""
    Write-Host "Logged out from Docker Hub." -ForegroundColor Cyan
} else {
    Write-Host ""
    Write-Host "❌ FAILED! Docker Hub login unsuccessful." -ForegroundColor Red
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host $loginResult -ForegroundColor Red
    Write-Host ""
    Write-Host "Please check:" -ForegroundColor Yellow
    Write-Host "1. Username is correct (not email)" -ForegroundColor Yellow
    Write-Host "2. Token is a Personal Access Token (starts with dckr_pat_)" -ForegroundColor Yellow
    Write-Host "3. Token has Read & Write permissions" -ForegroundColor Yellow
    Write-Host "4. Token hasn't expired" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== Test Complete ===" -ForegroundColor Cyan
