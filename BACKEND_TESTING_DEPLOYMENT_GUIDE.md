# Backend Testing & Deployment Guide

## Overview
This project uses automated testing and deployment for the Laravel backend.

## How It Works

### 🔍 On Every Pull Request
When you create a PR, the workflow:
1. **Checks for backend changes** - Only runs if `backend-laravel/` folder has modifications
2. **Runs automated tests** - PHPUnit tests with PostgreSQL database
3. **Reports results** - Shows test results in the PR

### 🚀 On Push to Main/Clean Branch
When backend changes are merged:
1. **Runs all tests first** - Ensures code quality
2. **Deploys to EC2 automatically** - Updates production server via SSH
3. **Runs migrations** - Updates database schema
4. **Optimizes Laravel** - Caches configs, routes, and views

## Running Tests Locally

### Quick Test
```bash
cd backend-laravel
php artisan test
```

### With Coverage
```bash
php artisan test --coverage
```

### Specific Test
```bash
php artisan test --filter=HealthCheckTest
```

### Parallel Testing (faster)
```bash
php artisan test --parallel
```

## Writing Tests

### Feature Tests (API Testing)
Location: `backend-laravel/tests/Feature/`

Example:
```php
<?php
namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class EmployeeApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_create_employee(): void
    {
        $response = $this->postJson('/api/v1/employees/create-with-face', [
            'name' => 'John Doe',
            'email' => 'john@example.com',
            'employee_id' => 'EMP001'
        ]);

        $response->assertStatus(201);
        $response->assertJsonStructure(['data' => ['id', 'name', 'email']]);
    }
}
```

### Unit Tests
Location: `backend-laravel/tests/Unit/`

Example:
```php
<?php
namespace Tests\Unit;

use PHPUnit\Framework\TestCase;
use App\Models\Employee;

class EmployeeTest extends TestCase
{
    public function test_employee_full_name(): void
    {
        $employee = new Employee(['first_name' => 'John', 'last_name' => 'Doe']);
        $this->assertEquals('John Doe', $employee->full_name);
    }
}
```

## Manual Deployment

### Deploy via SSH
```bash
ssh user@your-ec2-server
cd /var/www/html/aegis-ignis/backend-laravel
git pull origin main
composer install --no-dev --optimize-autoloader
php artisan migrate --force
php artisan optimize
```

### Or use the workflow manually
Go to GitHub Actions → Backend PR Tests & Deploy → Run workflow

## Required GitHub Secrets

For deployment to work, configure these secrets in your repository:

| Secret | Description | Example |
|--------|-------------|---------|
| `EC2_SSH_KEY` | Private SSH key for EC2 | Your private key content |
| `EC2_HOST` | EC2 server IP or domain | `35.180.117.85` |
| `EC2_USER` | SSH username | `ubuntu` or `ec2-user` |
| `DEPLOY_PATH` | Application path on server | `/var/www/html/aegis-ignis` |

### Setting up SSH access:
1. Generate SSH key pair on EC2:
   ```bash
   ssh-keygen -t ed25519 -C "github-actions"
   ```
2. Add public key to `~/.ssh/authorized_keys` on EC2
3. Add private key to GitHub repository secrets as `EC2_SSH_KEY`

## Workflow Triggers

### When does it run?
- ✅ Pull request to `main` or `clean` with backend changes
- ✅ Push to `main` or `clean` with backend changes
- ✅ Manual trigger from GitHub Actions

### What does it skip?
- ❌ PRs without backend changes
- ❌ Changes only in frontend folders
- ❌ PRs (won't deploy, only test)

## Test Database

Tests use SQLite in-memory database by default for speed.
For more realistic tests, the CI uses PostgreSQL.

## Troubleshooting

### Tests failing locally?
```bash
# Clear caches
php artisan config:clear
php artisan cache:clear

# Regenerate key
php artisan key:generate

# Run tests
php artisan test
```

### Deployment failing?
- Check GitHub Actions logs
- Verify SSH secrets are correct
- Ensure EC2 has proper permissions
- Check Laravel logs on server: `storage/logs/laravel.log`

## Best Practices

1. **Write tests for new features** - Add tests when adding API endpoints
2. **Run tests before committing** - `php artisan test`
3. **Check PR test results** - Don't merge failed tests
4. **Monitor deployments** - Watch GitHub Actions for deployment status
5. **Test migrations** - Run `php artisan migrate:fresh --seed` locally first

## Example Workflow

1. Create feature branch: `git checkout -b feature/new-endpoint`
2. Write code and tests
3. Run tests locally: `php artisan test`
4. Commit and push
5. Create PR → Tests run automatically
6. Fix any failing tests
7. Get PR approved
8. Merge to main → Automatic deployment!

---

**Need help?** Check the logs in GitHub Actions or run `php artisan test --help`
