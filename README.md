<img src="./readme/card-titles/title1.svg"/>

<br><br>

## License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

<br><br>


<!-- project overview -->
<img src="./readme/card-titles/title2.svg"/>

> Aegis-Ignis is an intelligent smart building security system that combines real-time fire detection, face recognition, and occupancy monitoring 
>The system provides instant visibility, intelligent alerts, and rapid emergency response through a unified platform that keeps people safe and assets protected.

<br><br>

<!-- System Design -->
<img src="./readme/card-titles/title3.svg"/>

### System Architecture

<img src="./readme/sql/schema.jpg "/>

<br><br>

<img src="./readme/sql/Microserevces.png "/>

```

### Technology Stack

| Component | Technology |
|-----------|-----------|
| **Backend** | Laravel 10, PostgreSQL |
| **Face Recognition** | Python, FastAPI, InsightFace |
| **Fire Detection** | Python, FastAPI, YOLOv8, OpenCV |
| **Frontend** | React, TypeScript, Vite, Tailwind CSS |
| **ML Framework** | Ultralytics YOLOv8, PyTorch |
| **Workflow Automation** | N8N |
| **Communication** | Twilio (WhatsApp, SMS, Voice) |
| **Real-time** | WebSockets, Server-Sent Events |

<br><br>

<!-- Project Highlights -->
<img src="./readme/card-titles/title4.svg"/>

### Core Features

- **Real-time Fire Detection**: ML-powered YOLOv8 model with color-based fallback detection running at 15 FPS for instant fire and smoke detection
- **Face Recognition System**: Fast employee identification using InsightFace embeddings with duplicate detection and caching for instant responses
- **Occupancy Monitoring**: Real-time tracking of people on each floor with automatic presence updates and evacuation alerts
- **Multi-Channel Alerts**: WhatsApp, SMS, and voice call notifications through N8N workflows with intelligent routing based on alert severity
- **Smart Building Dashboard**: Comprehensive web interface for monitoring cameras, floors, alerts, and employee presence in real-time
- **Employee Registration Portal**: Streamlined face registration system with photo upload and automatic embedding generation

### Key Capabilities

| Feature | Description |
|---------|-------------|
| **ML Fire Detection** | YOLOv8 model trained on fire/smoke datasets with 85%+ accuracy, fallback to HSV color detection |
| **Face Recognition** | Sub-second employee identification with duplicate prevention and cached embeddings |
| **Real-time Monitoring** | Live camera feeds with 15 FPS processing, floor-by-floor occupancy tracking |
| **Emergency Response** | Automatic alerts with people count, floor location, and evacuation instructions |
| **Multi-floor Support** | Scalable architecture supporting unlimited floors and cameras per building |

<br><br>

<!-- Demo -->
<img src="./readme/card-titles/title5.svg"/>

### System Screenshots

| Dashboard Overview | Floor Monitoring | Camera Management |
| --------------------------------------- | ------------------------------------- | ------------------------------------- |
| ![Dashboard](./readme/demo/1440x1024.png) | *Coming Soon* | *Coming Soon* |

| Fire Alerts | Employee Management | Face Registration |
| --------------------------------------- | ------------------------------------- | ------------------------------------- |
| *Coming Soon* | *Coming Soon* | *Coming Soon* |

<br><br>

<!-- Development & Testing -->
<img src="./readme/card-titles/title6.svg"/>

### Development Setup

#### Prerequisites
- PHP 8.1+ with Composer
- Python 3.10+
- PostgreSQL 14+
- Node.js 18+ with npm
- Docker (optional, for PostgreSQL)

#### Quick Start

```bash
# Clone repository
git clone <repository-url>
cd Aegis-IgnisGit

# Start all services (Windows)
START-ALL.bat

# Or start manually:
# 1. Start Laravel backend
cd backend-laravel
composer install
php artisan migrate
php artisan serve

# 2. Start Face Recognition Service
cd python-face-service
pip install -r requirements.txt
python main_fast.py

# 3. Start Fire Detection Service
cd fire-detection-service
pip install -r requirements.txt
python main.py

# 4. Start Frontend Dashboard
cd "Smart Building Dashboard Design"
npm install
npm run dev
```

### Testing

| CI/CD Pipeline | Test Coverage |
| --------------------------------------- | ------------------------------------- |
| *GitHub Actions* | *Laravel PHPUnit Tests* |

- **Backend tests**: `cd backend-laravel && php artisan test`
- **Python services**: Unit tests for ML models and detection algorithms
- **Frontend tests**: React component testing with Vitest

<br><br>

### Machine Learning Development

#### Fire Detection Model

- **Model**: YOLOv8 (YOLOv8n, YOLOv8s, YOLOv8m variants)
- **Training Dataset**: 900+ images expanded to 20,000+ using augmentation
- **Dataset Split**: 80/20 training/validation split
- **Performance**: 
  - mAP50: 0.75-0.90
  - Precision: 0.80-0.95
  - Recall: 0.75-0.90
  - Inference Speed: 10-30ms per frame (GPU)

#### Model Training Process

1. **Dataset Preparation**: Roboflow dataset download and validation
2. **Data Augmentation**: Copula-based augmentation with perturbation and noise
3. **Training**: 10-fold cross-validation with early stopping
4. **Model Serving**: FastAPI endpoint with MLFlow model registry integration

#### Face Recognition

- **Model**: InsightFace (ArcFace architecture)
- **Embedding Dimension**: 512-dimensional vectors
- **Performance**: Sub-second identification with 99%+ accuracy
- **Features**: Duplicate detection, caching, batch processing

| Training Dataset | Model Performance | Deployment |
| --------------------------------------- | ------------------------------------- | ------------------------------------- |
| *Fire Detection Dataset* | *YOLOv8 Metrics* | *FastAPI Endpoint* |

<br><br>

### MLOps (MLFlow)

- Model artifacts and training runs tracked using MLFlow
- Model versioning and registry for production deployments
- FastAPI endpoints serving registered models
- Automatic model validation and performance monitoring

| Model Registry | Training Metrics | Model Serving |
| --------------------------------------- | ------------------------------------- | ------------------------------------- |
| *MLFlow Dashboard* | *Training Graphs* | *FastAPI Endpoints* |

<br><br>

### N8N Workflow Automation

The system uses N8N for intelligent alert routing and multi-channel notifications:

- **Webhook Trigger**: Receives fire alerts from Alert Manager
- **Alert Type Routing**: 
  - `FIRE_EMERGENCY`: Standard fire detection alerts
  - `CRITICAL_EVACUATION`: Alerts when people are present on floor
  - `PRESENCE_UPDATE`: Regular occupancy updates
- **Multi-Channel Delivery**: WhatsApp, SMS, Voice calls based on severity
- **Backend Integration**: Automatic logging and alert history updates

Workflow configuration available in `n8n-workflow-fire-alert.json`

<br><br>

### API Documentation

#### Swagger/OpenAPI

- **Laravel Backend**: Available at `http://localhost:8000/api/documentation` (when configured)
- **Face Recognition Service**: Available at `http://localhost:8001/docs`
- **Fire Detection Service**: Available at `http://localhost:8002/docs`

#### Key Endpoints

**Laravel Backend (Port 8000)**
```
GET    /api/v1/cameras              # List all cameras
POST   /api/v1/cameras              # Add new camera
GET    /api/v1/floors               # List all floors
GET    /api/v1/alerts               # Get fire alerts
POST   /api/v1/alerts/fire          # Create fire alert
GET    /api/v1/employees            # List employees
POST   /api/v1/employees            # Register employee
GET    /api/v1/presence/floor-live/{id}  # Real-time floor occupancy
```

**Face Recognition Service (Port 8001)**
```
POST   /recognize                   # Recognize face from image
POST   /register                   # Register new face
GET    /health                     # Service health check
```

**Fire Detection Service (Port 8002)**
```
POST   /detect-fire                # Detect fire in image
GET    /health                     # Service health check
GET    /config                     # Get detection configuration
```

<br><br>

<!-- Extras -->
<img src="./readme/card-titles/title7.svg"/>

### Additional Tools & Services

| Tool | Purpose |
|------|---------|
| **N8N** | Workflow automation for multi-channel alerts |
| **Twilio** | WhatsApp, SMS, and Voice call integration |
| **MLFlow** | ML model tracking and registry |
| **PostgreSQL** | Primary database for all system data |
| **Docker** | Containerized PostgreSQL deployment |

### Project Structure

```
Aegis-IgnisGit/
├── backend-laravel/          # Laravel REST API backend
├── python-face-service/       # Face recognition microservice
├── fire-detection-service/     # Fire detection microservice
├── camera-detection-service/  # Camera stream processing
├── Smart Building Dashboard Design/  # React frontend dashboard
├── face-registration/         # Employee registration portal
├── ml_models/                 # ML model training and inference
│   ├── train/                # YOLOv8 training scripts
│   └── inference/            # Model inference code
├── services/                 # Shared Python services
│   ├── alert_manager.py      # Alert management and N8N integration
│   └── ml_fire_detector.py   # ML fire detection service
└── readme/                    # Documentation assets
```

### Environment Configuration

Key environment variables required:

```env
# Laravel Backend
DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_DATABASE=aegis_ignis

# Twilio (Alerts)
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
TWILIO_WHATSAPP_TO=whatsapp:+1234567890

# N8N Webhook
N8N_WEBHOOK_URL=http://localhost:5678/webhook/fire-alert

# Service URLs
FACE_SERVICE_URL=http://localhost:8001
FIRE_SERVICE_URL=http://localhost:8002
```

<br><br>

### Deployment

#### Production Deployment

1. **Backend**: Deploy Laravel to AWS EC2 or similar
2. **Python Services**: Deploy as systemd services or Docker containers
3. **Frontend**: Build and deploy React app to CDN or static hosting
4. **Database**: PostgreSQL on managed service (AWS RDS, etc.)
5. **N8N**: Deploy N8N instance for workflow automation

#### Docker Deployment (Optional)

```bash
# Start PostgreSQL
docker-compose -f docker/docker-compose.yml up -d postgres

# Run migrations
cd backend-laravel
php artisan migrate
```

<br><br>

### Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Code Standards

- **PHP**: Follow PSR-12 coding standards
- **Python**: Follow PEP 8 style guide
- **TypeScript/React**: Use ESLint and Prettier configurations
- **Commits**: Use conventional commit messages

<br><br>

### Support & Documentation

- **Architecture Details**: See [ARCHITECTURE.md](ARCHITECTURE.md)
- **Backend Setup**: See [backend-laravel/README_UNIFIED_BACKEND.md](backend-laravel/README_UNIFIED_BACKEND.md)
- **Fire Detection Training**: See [ml_models/train/README.md](ml_models/train/README.md)

<br><br>

---

**Aegis-Ignis** - Intelligent Smart Building Security System

*Protecting buildings, one detection at a time.*
