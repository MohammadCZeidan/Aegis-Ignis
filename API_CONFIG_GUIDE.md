# API Configuration Guide

All API base URLs are now centralized in environment files that are **git-ignored** to allow different configurations for development, staging, and production.

## Setup Instructions

### 1. Frontend (Smart Building Dashboard Design)

```bash
cd "Smart Building Dashboard Design"
cp .env.local.example .env.local
```

Edit `.env.local` with your API URLs:
- `VITE_BACKEND_API_URL` - Laravel backend API
- `VITE_FACE_SERVICE_URL` - Face detection service  
- `VITE_FIRE_SERVICE_URL` - Fire detection service
- `VITE_FLOOR_SERVICE_URL` - Floor monitoring service
- `VITE_CAMERA_SERVICE_URL` - Camera service

**Usage in code:**
```typescript
import { API_CONFIG, buildBackendUrl, getStorageUrl } from '@/config/api';

// Use the config
fetch(buildBackendUrl('/cameras'));
fetch(`${API_CONFIG.FIRE_SERVICE}/detect-fire`);
const imageUrl = getStorageUrl('photos/image.jpg');
```

### 2. Backend (Laravel)

Copy `.env.services.example` to `.env.services` and update service URLs, then include it in your main `.env`:

```bash
cd backend-laravel
cp .env.services.example .env.services
# Edit .env.services with your service URLs
```

Add to your `.env`:
```
# Service URLs
FIRE_SERVICE_URL=http://localhost:8002
FACE_SERVICE_URL=http://localhost:8001
FLOOR_SERVICE_URL=http://localhost:8003
CAMERA_SERVICE_URL=http://localhost:5000
```

### 3. Python Services

Each service has its own `.env`:

**Face Detection Service:**
```bash
cd python-face-service
cp .env.example .env
# Edit .env with BACKEND_API_URL and PORT
```

**Fire Detection Service:**
```bash
cd fire-detection-service  
cp .env.example .env
# Edit .env with BACKEND_API_URL and PORT
```

**Camera Detection Service:**
```bash
cd camera-detection-service
cp .env.example .env
# Edit .env with BACKEND_API_URL and service URLs
```

## Environment Files Summary

| File | Status | Purpose |
|------|--------|---------|
| `.env` | Git-ignored | Your local configuration |
| `.env.example` | Git-tracked | Template for team members |
| `.env.local` | Git-ignored | Frontend local config (Vite) |
| `.env.services` | Git-ignored | Backend service URLs |

## Production Deployment

For production (EC2), create `.env` files with production URLs:

**Frontend `.env.local`:**
```bash
VITE_BACKEND_API_URL=http://35.180.117.85/api/v1
VITE_FACE_SERVICE_URL=http://35.180.117.85:8001
VITE_FIRE_SERVICE_URL=http://35.180.117.85:8002
# etc...
```

**Services `.env`:**
```bash
BACKEND_API_URL=http://35.180.117.85/api/v1
```

## GitHub Actions / CI/CD

Environment variables are set via GitHub Secrets and injected during deployment. See `.github/workflows/deploy.yml` for details.
