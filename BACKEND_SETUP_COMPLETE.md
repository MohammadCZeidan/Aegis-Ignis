# ✅ Backend Testing & Deployment Setup Complete!

## What Was Created

### 🧪 Testing Infrastructure
1. **PHPUnit Configuration** (`phpunit.xml`)
   - SQLite in-memory database for fast tests
   - Proper test environment settings

2. **Test Files**
   - `tests/TestCase.php` - Base test class
   - `tests/CreatesApplication.php` - Application bootstrapper
   - `tests/Feature/HealthCheckTest.php` - API health tests
   - `tests/Feature/Api/FloorApiTest.php` - Floor API tests
   - `tests/Feature/Api/CameraApiTest.php` - Camera API tests
   - `tests/Unit/ExampleTest.php` - Example unit test

3. **Test Commands in composer.json**
   ```bash
   composer test           # Run all tests
   composer test-parallel  # Run tests in parallel (faster)
   composer test-coverage  # Run with coverage report
   ```

### 🚀 GitHub Actions Workflow
**File:** `.github/workflows/backend-pr-deploy.yml`

**Features:**
- ✅ Only runs when backend files change
- ✅ Runs on every PR to main/clean
- ✅ Runs automated tests with PostgreSQL
- ✅ Deploys to EC2 after merge (SSH)
- ✅ Runs migrations automatically
- ✅ Optimizes Laravel after deployment

**Workflow Steps:**
1. Check if `backend-laravel/` has changes
2. If yes → Run PHPUnit tests
3. If tests pass + pushed to main → Deploy via SSH
4. Run migrations on server
5. Clear and cache configs

### 📝 Documentation
1. `BACKEND_TESTING_DEPLOYMENT_GUIDE.md` - Complete guide
2. `BACKEND_QUICK_REFERENCE.md` - Quick commands
3. `GITHUB_SECRETS_SETUP.md` - How to configure secrets

### 🛠️ Helper Scripts
1. `SETUP-BACKEND.bat` - Install dependencies
2. `RUN-BACKEND-TESTS.bat` - Run tests quickly

---

## 🎯 How To Use

### First Time Setup
```bash
# Run setup script (installs composer dependencies)
.\SETUP-BACKEND.bat
```

### Write & Run Tests
```bash
# Run all tests
cd backend-laravel
php artisan test

# Or use the shortcut
.\RUN-BACKEND-TESTS.bat

# Run specific test
php artisan test --filter=HealthCheckTest
```

### Create a Pull Request
```bash
# 1. Create feature branch
git checkout -b feature/new-api-endpoint

# 2. Make changes in backend-laravel/

# 3. Write tests for your changes

# 4. Run tests locally
php artisan test

# 5. Commit and push
git add .
git commit -m "Add new API endpoint with tests"
git push origin feature/new-api-endpoint

# 6. Create PR on GitHub
# → Tests run automatically
# → Check results in PR
```

### After PR is Merged
- GitHub Actions automatically:
  1. Runs tests again
  2. Deploys to EC2 via SSH
  3. Runs migrations
  4. Optimizes Laravel

---

## 🔐 GitHub Secrets Required

Set these in: **GitHub Repository → Settings → Secrets → Actions**

| Secret | Example Value | Description |
|--------|---------------|-------------|
| `EC2_SSH_KEY` | `-----BEGIN OPENSSH PRIVATE KEY-----...` | Private SSH key |
| `EC2_HOST` | `35.180.117.85` | Server IP or domain |
| `EC2_USER` | `ubuntu` | SSH username |
| `DEPLOY_PATH` | `/var/www/html/aegis-ignis` | App path on server |

**Guide:** See `GITHUB_SECRETS_SETUP.md` for detailed setup instructions.

---

## 📊 Example Test

```php
<?php
namespace Tests\Feature\Api;

use Tests\TestCase;
use Illuminate\Foundation\Testing\RefreshDatabase;

class EmployeeApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_can_get_next_employee_id(): void
    {
        $response = $this->getJson('/api/v1/employees/next-id');
        
        $response->assertStatus(200);
        $response->assertJsonStructure(['employee_id']);
    }

    public function test_can_create_employee_with_face(): void
    {
        $response = $this->postJson('/api/v1/employees/create-with-face', [
            'name' => 'John Doe',
            'email' => 'john@example.com',
            'employee_id' => 'EMP001',
            'phone' => '1234567890'
        ]);

        $response->assertStatus(201);
        $this->assertDatabaseHas('employees', [
            'email' => 'john@example.com'
        ]);
    }
}
```

---

## 🎬 Workflow in Action

### Scenario: Add New Endpoint

1. **Create feature branch**
   ```bash
   git checkout -b feature/employee-stats
   ```

2. **Add new route** (routes/api.php)
   ```php
   Route::get('/employees/stats', [EmployeeController::class, 'stats']);
   ```

3. **Add controller method**
   ```php
   public function stats()
   {
       return response()->json([
           'total' => Employee::count(),
           'active' => Employee::where('status', 'active')->count()
       ]);
   }
   ```

4. **Write test** (tests/Feature/Api/EmployeeApiTest.php)
   ```php
   public function test_can_get_employee_stats(): void
   {
       $response = $this->getJson('/api/v1/employees/stats');
       
       $response->assertStatus(200);
       $response->assertJsonStructure(['total', 'active']);
   }
   ```

5. **Run tests locally**
   ```bash
   php artisan test --filter=test_can_get_employee_stats
   ```

6. **Commit and push**
   ```bash
   git add .
   git commit -m "Add employee statistics endpoint"
   git push origin feature/employee-stats
   ```

7. **Create PR** → Tests run automatically!

8. **Merge PR** → Automatically deploys to EC2!

---

## 🔄 CI/CD Flow

```
┌─────────────────────┐
│  Create PR          │
│  (backend changes)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  GitHub Actions     │
│  Detects Changes    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Run PHPUnit Tests  │
│  with PostgreSQL    │
└──────────┬──────────┘
           │
      ✅ Pass ❌ Fail
           │         │
           │         └──> Fix & Push
           ▼
┌─────────────────────┐
│  PR Review          │
│  & Approval         │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Merge to Main      │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Run Tests Again    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  SSH to EC2         │
│  Deploy Laravel     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  Run Migrations     │
│  Optimize Cache     │
└──────────┬──────────┘
           │
           ▼
      🎉 DEPLOYED!
```

---

## 🚨 Troubleshooting

### Tests Won't Run
```bash
# Install dependencies
cd backend-laravel
composer install

# Clear caches
php artisan config:clear
php artisan cache:clear

# Try again
php artisan test
```

### Deployment Fails
- Check GitHub Actions logs (detailed errors)
- Verify all 4 secrets are set correctly
- Test SSH manually: `ssh ubuntu@35.180.117.85`
- Check server logs: `ssh ubuntu@35.180.117.85 'tail -f /var/www/html/aegis-ignis/backend-laravel/storage/logs/laravel.log'`

### Workflow Not Triggering
- Ensure changes are in `backend-laravel/` folder
- Check workflow file is in `.github/workflows/`
- Verify PR target is `main` or `clean` branch

---

## 📈 Benefits

✅ **Automatic Testing** - Every PR is tested before merge
✅ **No Breaking Changes** - Tests catch bugs early
✅ **Automatic Deployment** - No manual SSH needed
✅ **Fast Feedback** - Know if tests pass within minutes
✅ **Safe Deployments** - Only deploys if tests pass
✅ **Migration Safety** - Migrations run automatically
✅ **Zero Downtime** - Laravel optimized after deploy

---

## 🎓 Next Steps

1. **Run Setup** - `.\SETUP-BACKEND.bat`
2. **Test It** - `.\RUN-BACKEND-TESTS.bat`
3. **Add Secrets** - Configure GitHub secrets
4. **Create Test PR** - Make a small backend change
5. **Watch It Work** - See GitHub Actions in action!

---

**Need Help?**
- Read: `BACKEND_TESTING_DEPLOYMENT_GUIDE.md`
- Quick Commands: `BACKEND_QUICK_REFERENCE.md`
- Setup Secrets: `GITHUB_SECRETS_SETUP.md`

Your backend is now production-ready with CI/CD! 🚀
