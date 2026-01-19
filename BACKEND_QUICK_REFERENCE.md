# 🚀 Quick Reference - Backend Testing & Deployment

## Run Tests Locally

```bash
# Feature tests only
cd backend-laravel
php artisan test

# Or use composer
composer test

# Windows shortcut
.\RUN-BACKEND-TESTS.bat
```

## How the Workflow Works

### 1️⃣ **Create PR with Backend Changes**
```bash
git checkout -b feature/my-backend-feature
# Make changes in backend-laravel/
git add .
git commit -m "Add new API endpoint"
git push origin feature/my-backend-feature
```

### 2️⃣ **On Pull Request - CI Runs Tests**
- ✅ Detects changes in `backend-laravel/`
- ✅ Runs all feature tests
- ✅ Shows results in PR
- ❌ Does NOT deploy (tests only)

### 3️⃣ **After PR Merged - CD Deploys**
- ✅ SSH to EC2
- ✅ Git pull latest code
- ✅ Composer install
- ✅ Run migrations
- ✅ Optimize Laravel
- ✅ Done!

## Required GitHub Secrets

Set these in: **Settings → Secrets and variables → Actions**

```
EC2_SSH_KEY     → Your private SSH key
EC2_HOST        → 35.180.117.85
EC2_USER        → ubuntu (or your SSH user)
DEPLOY_PATH     → /var/www/html/aegis-ignis
```

## Workflow Triggers

| Event | Action |
|-------|--------|
| PR to main/clean (backend changes) | Run feature tests |
| Push to main/clean (backend changes) | Deploy to EC2 via SSH |
| No backend changes | Skip workflow |

## Test Examples

### Feature Test (API Testing)
```php
// tests/Feature/Api/EmployeeApiTest.php
public function test_can_create_employee(): void
{
    $response = $this->postJson('/api/v1/employees', [
        'name' => 'John Doe',
        'email' => 'john@example.com'
    ]);

    $response->assertStatus(201);
}
```

### Run Specific Test
```bash
php artisan test --filter=test_can_create_employee
```

## Manual Deployment

### Option 1: SSH Directly
```bSSH and Update
```bash
ssh ubuntu@35.180.117.85
cd /var/www/html/aegis-ignis
git pull origin main
cd backend-laravel
composer install --no-dev --optimize-autoloader
php artisan migrate --force
php artisan optimize
```
## Troubleshooting

### Tests Failing?
```bash
cd backend-laravel
php artisan config:clear
php artisan cache:clear
composer dump-autoload
php artisan test
```

### Check Test Output
```bash
php artisan test --verbose
```

### Deployment Failed?
- Check GitHub Actions logs
- Verify secrets are set correctly
- Check server: `ssh ubuntu@35.180.117.85 'cd /var/www/html/aegis-ignis && git status'`

---

**📚 Full Guide:** See [BACKEND_TESTING_DEPLOYMENT_GUIDE.md](BACKEND_TESTING_DEPLOYMENT_GUIDE.md)
