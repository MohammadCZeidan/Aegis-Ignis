# 🎯 AEGIS-IGNIS - Unified Laravel Backend

**One Backend to Rule Them All!**

This is your **single, unified Laravel backend**. Everything is managed and controlled through Laravel, making it easy to develop, deploy, and maintain.

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│     Laravel Backend (Main)             │
│     Port: 8000                         │
│  ┌─────────────────────────────────┐  │
│  │  • All API Endpoints            │  │
│  │  • Database (PostgreSQL)         │  │
│  │  • Authentication (Sanctum)      │  │
│  │  • Business Logic (Services)     │  │
│  │  • Form Requests (Validation)    │  │
│  │  • Service Management Commands   │  │
│  └─────────────────────────────────┘  │
└──────────────┬────────────────────────┘
               │
        ┌──────┴──────┐
        │            │
        ↓            ↓
┌──────────────┐  ┌──────────────┐
│ Python Face  │  │ Python Fire  │
│ Service      │  │ Detection    │
│ (Port 8001)  │  │ (Port 8002)  │
│              │  │              │
│ Managed by   │  │ Managed by   │
│ Laravel      │  │ Laravel      │
└──────────────┘  └──────────────┘
```

## ✨ Key Features

### 🎯 Single Entry Point
- **Everything starts from Laravel**
- One command to start all services
- Unified configuration
- Centralized logging

### 🧹 Clean Architecture
- **Form Requests** - All validation in separate files
- **Services** - All business logic in service classes
- **Controllers** - Thin controllers, just HTTP handling
- **Commands** - Service management through Artisan

### 🚀 Easy Management
- Start/stop services with Laravel commands
- Check service status
- Health monitoring
- Automatic dependency management

## 📦 Installation

1. **Install PHP dependencies:**
```bash
cd backend-laravel
composer install
```

2. **Configure environment:**
```bash
cp .env.example .env
php artisan key:generate
```

3. **Set up database:**
```bash
php artisan migrate
php artisan db:seed
```

## 🚀 Quick Start

### Option 1: Start Everything (Recommended)
```bash
# Windows
.\start-all.ps1

# Linux/Mac
./start-all.sh
```

### Option 2: Start from Laravel
```bash
# Start Laravel
php artisan serve

# In another terminal, start Python services
php artisan services:start --all
```

### Option 3: Manual Start
```bash
# Start Laravel
php artisan serve

# Start Face Service
php artisan services:start --face

# Start Fire Detection
php artisan services:start --fire
```

## 🎮 Laravel Artisan Commands

### Service Management
```bash
# Start all Python services
php artisan services:start --all

# Start specific service
php artisan services:start --face
php artisan services:start --fire

# Stop services
php artisan services:stop --all
php artisan services:stop --face
php artisan services:stop --fire

# Check service status
php artisan services:status
```

### Database
```bash
# Run migrations
php artisan migrate

# Seed database
php artisan db:seed

# Refresh database
php artisan migrate:fresh --seed
```

### Development
```bash
# Clear cache
php artisan cache:clear
php artisan config:clear
php artisan route:clear

# Generate optimized autoloader
composer dump-autoload -o
```

## 📁 Project Structure

```
backend-laravel/
├── app/
│   ├── Console/
│   │   └── Commands/          # Artisan commands
│   │       ├── StartServices.php
│   │       ├── StopServices.php
│   │       └── ServiceStatus.php
│   ├── Http/
│   │   ├── Controllers/        # Thin controllers
│   │   │   └── Api/
│   │   └── Requests/           # Form validation
│   │       ├── LoginRequest.php
│   │       ├── RegisterRequest.php
│   │       └── ...
│   └── Services/               # Business logic
│       ├── AuthService.php
│       ├── EmployeeService.php
│       ├── FloorService.php
│       ├── CameraService.php
│       ├── FireDetectionService.php
│       ├── AlertService.php
│       └── OccupancyService.php
├── config/
│   └── services.php            # Microservice config
├── routes/
│   └── api.php                 # API routes
└── README_UNIFIED_BACKEND.md   # This file
```

## 🔌 API Endpoints

All endpoints are under `/api/v1/`:

### Authentication
- `POST /api/v1/auth/login/json` - Login
- `POST /api/v1/auth/register` - Register
- `GET /api/v1/auth/me` - Get current user

### Employees
- `GET /api/v1/employees` - List employees
- `GET /api/v1/employees/by-floor/{floorId}` - Get by floor
- `POST /api/v1/employees/register-face` - Register with face
- `DELETE /api/v1/employees/{id}` - Delete employee

### Floors
- `GET /api/v1/floors` - List floors
- `GET /api/v1/floors/{id}` - Get floor
- `POST /api/v1/floors` - Create floor
- `PUT /api/v1/floors/{id}` - Update floor
- `DELETE /api/v1/floors/{id}` - Delete floor

### Cameras
- `GET /api/v1/cameras` - List cameras
- `GET /api/v1/cameras/{id}` - Get camera
- `POST /api/v1/cameras` - Create camera
- `PUT /api/v1/cameras/{id}` - Update camera
- `DELETE /api/v1/cameras/{id}` - Delete camera

### Fire Detection
- `POST /api/v1/fire-detections/report` - Report detection (public)
- `GET /api/v1/fire-detections` - List events
- `GET /api/v1/fire-detections/{id}` - Get event
- `POST /api/v1/fire-detections/{id}/resolve` - Resolve event

### Alerts
- `GET /api/v1/alerts` - List alerts
- `GET /api/v1/alerts/{id}` - Get alert
- `POST /api/v1/alerts/{id}/acknowledge` - Acknowledge alert

### Occupancy
- `GET /api/v1/occupancy/summary` - Get summary
- `GET /api/v1/occupancy/floors/{floorId}` - Get by floor

### Health
- `GET /health` - Full health check
- `GET /ping` - Quick health check

## 🔧 Configuration

### Environment Variables (.env)
```env
# Application
APP_NAME=Aegis-Ignis
APP_ENV=local
APP_DEBUG=true

# Database
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=aegis_ignis
DB_USERNAME=your_username
DB_PASSWORD=your_password

# Microservices
FACE_SERVICE_URL=http://localhost:8001
FIRE_SERVICE_URL=http://localhost:8002
MICROSERVICE_TIMEOUT=10
MICROSERVICE_MAX_RETRIES=3
```

## 🧪 Testing

```bash
# Run tests
php artisan test

# Run specific test
php artisan test --filter AuthTest
```

## 📝 Code Style

This project follows Laravel best practices:
- **PSR-12** coding standards
- **Form Requests** for validation
- **Services** for business logic
- **Thin Controllers** for HTTP handling
- **Dependency Injection** throughout

## 🚨 Troubleshooting

### Services won't start
```bash
# Check Python is installed
python --version

# Check service status
php artisan services:status

# Check ports are available
netstat -ano | findstr :8001  # Windows
lsof -i :8001                # Linux/Mac
```

### Database connection issues
```bash
# Test database connection
php artisan tinker
>>> DB::connection()->getPdo();

# Run migrations
php artisan migrate:fresh --seed
```

## 📚 Documentation

- [Laravel Documentation](https://laravel.com/docs)
- [API Documentation](./README.md)
- [Architecture Guide](../BACKEND_ARCHITECTURE.md)

## 🎯 Why This Architecture?

1. **Single Source of Truth** - Laravel is the main backend
2. **Clean Code** - Separation of concerns (Requests, Services, Controllers)
3. **Easy Management** - Everything controlled through Laravel
4. **Scalable** - Can scale services independently
5. **Maintainable** - Clear structure, easy to understand

## 🤝 Contributing

1. Follow PSR-12 coding standards
2. Use Form Requests for validation
3. Put business logic in Services
4. Keep controllers thin
5. Write tests for new features

---

**Remember: This is ONE backend. Everything is managed through Laravel!** 🚀

