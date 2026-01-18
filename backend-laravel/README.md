# 🎯 Aegis-Ignis - Unified Laravel Backend

**One Backend to Rule Them All!**

This is your **single, unified Laravel backend** for the Smart Building Security & Fire Detection System. Everything is managed and controlled through Laravel.

> 📖 **For complete documentation, see [README_UNIFIED_BACKEND.md](./README_UNIFIED_BACKEND.md)**

## Prerequisites

- PHP 8.1+
- Composer
- PostgreSQL
- Redis (optional)

## Installation

1. **Install dependencies:**
```bash
composer install
```

2. **Configure environment:**
```bash
cp .env.example .env
php artisan key:generate
```

Edit `.env` file:
```env
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=aegis_ignis
DB_USERNAME=aegis_user
DB_PASSWORD=aegis_password
```

3. **Run migrations:**
```bash
php artisan migrate
```

4. **Seed database:**
```bash
php artisan db:seed
```

5. **Start development server:**
```bash
php artisan serve
```

6. **Start Python microservices (optional):**
```bash
# Start all services
php artisan services:start --all

# Or start individually
php artisan services:start --face
php artisan services:start --fire

# Check status
php artisan services:status
```

The API will be available at http://localhost:8000

> 💡 **Tip:** Use `php artisan start:all` for quick start instructions, or use the unified startup script `.\start-all.ps1` (Windows) / `./start-all.sh` (Linux/Mac)

## API Endpoints

### Authentication
- `POST /api/v1/auth/login/json` - Login
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/auth/me` - Get current user (requires auth)

### Employees
- `GET /api/v1/employees` - List employees
- `GET /api/v1/employees/by-floor/{floorId}` - Get employees by floor
- `POST /api/v1/employees/register-face` - Register employee with face
- `DELETE /api/v1/employees/{id}` - Delete employee

### Floors
- `GET /api/v1/floors` - List floors
- `GET /api/v1/floors/{id}` - Get floor details

### Cameras
- `GET /api/v1/cameras` - List cameras
- `GET /api/v1/cameras/{id}` - Get camera details

### Alerts
- `GET /api/v1/alerts` - List alerts
- `GET /api/v1/alerts/{id}` - Get alert details
- `POST /api/v1/alerts/{id}/acknowledge` - Acknowledge alert

### Occupancy
- `GET /api/v1/occupancy/summary` - Get occupancy summary
- `GET /api/v1/occupancy/floors/{floorId}` - Get occupancy by floor

## Default Credentials

- **Admin:** admin@aegis-ignis.com / admin123
- **User:** user@aegis-ignis.com / user123

## Face Recognition

The face recognition service is currently a placeholder. In production, you would:

1. **Option 1:** Call a Python microservice via HTTP/Queue
2. **Option 2:** Use a PHP extension for face recognition
3. **Option 3:** Use an external API service

The `FaceRecognitionService` class provides the interface. Update the `detectAndExtractFace()` method to integrate with your chosen solution.

## Testing

```bash
php artisan test
```

## Production Deployment

1. Set `APP_ENV=production` in `.env`
2. Set `APP_DEBUG=false`
3. Run `php artisan config:cache`
4. Run `php artisan route:cache`
5. Set up proper CORS origins
6. Configure queue workers for background jobs
7. Set up proper file storage (S3, etc.)

## Notes

- Face recognition currently returns mock embeddings. Integrate with Python service for production.
- File storage uses local disk. Configure S3 or other storage for production.
- Sanctum is used for API authentication.

