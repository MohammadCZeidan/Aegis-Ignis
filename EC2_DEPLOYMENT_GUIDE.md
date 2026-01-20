# EC2 Deployment Guide - Step by Step

## ✅ What We've Done
- Employee API now returns `photo_url` for all employees
- New endpoint: `GET /api/v1/employees/{id}/photo` returns base64 image
- CI/CD workflows fixed and ready
- All tests passing

## 📋 Prerequisites

### 1. GitHub Secrets Configuration
Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret

Add these 4 secrets:

| Secret Name | Value | Description |
|------------|-------|-------------|
| `EC2_SSH_KEY` | Your private SSH key | The private key to access EC2 |
| `EC2_HOST` | `35.180.227.44` | Your EC2 server IP |
| `EC2_USER` | `ubuntu` (or your user) | SSH username |
| `DEPLOY_PATH` | `/var/www/html/aegis-ignis` | Where your app lives on EC2 |

**To get your SSH private key:**
```bash
# On your local machine where you have EC2 access
cat ~/.ssh/your-ec2-key.pem
# Copy the ENTIRE output including -----BEGIN and -----END lines
```

---

## 🚀 EC2 Server Setup

### Step 1: Connect to EC2
```bash
ssh ubuntu@35.180.227.44 -i your-key.pem
```

### Step 2: Install Required Software

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install PHP 8.2 and extensions
sudo apt install -y software-properties-common
sudo add-apt-repository ppa:ondrej/php -y
sudo apt update
sudo apt install -y php8.2 php8.2-cli php8.2-fpm php8.2-mbstring php8.2-xml php8.2-pgsql php8.2-curl php8.2-zip php8.2-gd php8.2-intl php8.2-bcmath php8.2-redis

# Install Composer
curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer
curl -sS https://getcomposer.org/installer | sudo php -- --install-dir=/usr/local/bin --filename=composer

# Install PostgreSQL
sudo apt install -y postgresql postgresql-contrib

# Install Nginx
sudo apt install -y nginx

# Install Python 3.10
sudo apt install -y python3 python3-pip

# Install Redis
sudo apt install -y redis-server
sudo systemctl enable redis-server
sudo systemctl start redis-server

# Install Git
sudo apt install -y git
```

### Step 3: Setup PostgreSQL Database

```bash
sudo -u postgres psql

# In PostgreSQL prompt:
CREATE DATABASE aegis_ignis;
CREATE USER aegis_user WITH PASSWORD 'your_secure_password_here';
GRANT ALL PRIVILEGES ON DATABASE aegis_ignis TO aegis_user;

# Connect to the database and grant schema permissions
\c aegis_ignis
GRANT ALL ON SCHEMA public TO aegis_user;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO aegis_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO aegis_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO aegis_user;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO aegis_user;
\q
```

### Step 4: Clone Repository

```bash
# Create directory
sudo mkdir -p /var/www/html
cd /var/www/html

# Clone your repository
sudo git clone https://github.com/MohammadCZeidan/Aegis-Ignis.git aegis-ignis
cd aegis-ignis

# Checkout your branch
sudo git checkout clean

# Set permissions
sudo chown -R www-data:www-data /var/www/html/aegis-ignis
sudo chmod -R 755 /var/www/html/aegis-ignis
```

### Step 5: Setup Laravel Backend

```bash
cd /var/www/html/aegis-ignis/backend-laravel

# Install dependencies (include dev for now to avoid missing providers)
sudo -u www-data composer install --optimize-autoloader

# Create .env file and set proper permissions
sudo cp .env.example .env
sudo chown www-data:www-data .env
sudo chmod 664 .env
sudo nano .env
```

**Edit `.env` with these values:**
```env
APP_NAME="Aegis Ignis"
APP_ENV=production
APP_KEY=
APP_DEBUG=false
APP_URL=http://35.180.227.44

DB_CONNECTION=pgsql
DB_HOST=127.0.0.1
DB_PORT=5432
DB_DATABASE=aegis_ignis
DB_USERNAME=aegis_user
DB_PASSWORD=your_secure_password_here

CACHE_DRIVER=redis
SESSION_DRIVER=redis
QUEUE_CONNECTION=redis

REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379
```

**Generate application key and setup:**
```bash
# Clear any cached configs first
sudo -u www-data php artisan config:clear || true
sudo -u www-data php artisan cache:clear || true

# Generate key and run migrations
sudo -u www-data php artisan key:generate
sudo -u www-data php artisan migrate --force
sudo -u www-data php artisan db:seed --force
sudo -u www-data php artisan storage:link
sudo -u www-data php artisan config:cache
sudo -u www-data php artisan route:cache
# Note: view:cache skipped - API backend doesn't use Blade views

# Set permissions
sudo chown -R www-data:www-data /var/www/html/aegis-ignis/backend-laravel/storage
sudo chown -R www-data:www-data /var/www/html/aegis-ignis/backend-laravel/bootstrap/cache
sudo chmod -R 775 /var/www/html/aegis-ignis/backend-laravel/storage
sudo chmod -R 775 /var/www/html/aegis-ignis/backend-laravel/bootstrap/cache
```

### Step 6: Setup Nginx

```bash
sudo nano /etc/nginx/sites-available/aegis-ignis
```

**Paste ONLY the configuration below (don't include the ```nginx line):**
```nginx
server {
    listen 80;
    server_name 35.180.227.44;
    root /var/www/html/Aegis-Ignis/backend-laravel/public;

    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";

    index index.php;

    charset utf-8;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location = /favicon.ico { access_log off; log_not_found off; }
    location = /robots.txt  { access_log off; log_not_found off; }

    error_page 404 /index.php;

    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php8.2-fpm.sock;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }

    client_max_body_size 20M;
}
```

**Enable the site:**
```bash
sudo ln -s /etc/nginx/sites-available/aegis-ignis /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl reload nginx
```

### Step 7: Setup Python Services (OPTIONAL - Run Locally Instead)

**Note:** You can skip this step and run Python services locally using `START-ALL.bat`

If you want Python services on EC2:
```bash
cd /var/www/html/aegis-ignis

# Fire Detection Service
cd fire-detection-service
sudo pip3 install -r requirements.txt

# Face Recognition Service
cd ../python-face-service
sudo pip3 install -r requirements.txt
```

### Step 8: Setup Systemd Services (OPTIONAL - Only if running Python on EC2)

**Fire Detection Service:**
```bash
sudo nano /etc/systemd/system/fire-detection.service
```

```ini
[Unit]
Description=Fire Detection Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/html/aegis-ignis/fire-detection-service
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Face Recognition Service:**
```bash
sudo nano /etc/systemd/system/face-recognition.service
```

```ini
[Unit]
Description=Face Recognition Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/var/www/html/aegis-ignis/python-face-service
ExecStart=/usr/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable and start services:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable fire-detection
sudo systemctl enable face-recognition
sudo systemctl start fire-detection
sudo systemctl start face-recognition

# Check status
sudo systemctl status fire-detection
sudo systemctl status face-recognition
```

---

## 🔄 Using GitHub Actions for Deployment

### Manual Deployment (Recommended)

1. Go to your GitHub repository
2. Click **Actions** tab
3. Click **Backend CI/CD** workflow on the left
4. Click **Run workflow** button (top right)
5. Select branch: `clean` or `main`
6. Click **Run workflow**

**This will:**
- SSH into your EC2 server
- Pull latest code from GitHub
- Install composer dependencies
- Run migrations
- Optimize Laravel
- Set proper permissions

---

## 🧪 Testing Your Deployment

### 1. Test Backend API
```bash
curl http://35.180.227.44/api/health
curl http://35.180.227.44/api/v1/employees
curl http://35.180.227.44/api/v1/floors
```

### 2. Test Employee Photos
```bash
# Get employee with photos
curl http://35.180.227.44/api/v1/employees

# Get specific employee photo as base64
curl http://35.180.227.44/api/v1/employees/1/photo
```

### 3. Check Service Logs
```bash
# Laravel logs
sudo tail -f /var/www/html/aegis-ignis/backend-laravel/storage/logs/laravel.log

# Nginx logs
sudo tail -f /var/log/nginx/error.log

# Service logs
sudo journalctl -u fire-detection -f
sudo journalctl -u face-recognition -f
```

---

## 🎨 Frontend Setup

### Update Frontend Environment Variables

**face-registration/.env.production:**
```env
VITE_API_URL=http://35.180.227.44/api/v1
VITE_BACKEND_URL=http://35.180.227.44
```

**Smart Building Dashboard Design/.env.production:**
```env
VITE_API_URL=http://35.180.227.44/api/v1
VITE_FIRE_DETECTION_URL=http://localhost:5001
VITE_FACE_SERVICE_URL=http://localhost:8000
VITE_BACKEND_URL=http://35.180.227.44
```

**Note:** Python services (fire detection, face recognition) run locally via `START-ALL.bat`

### Build and Deploy Frontend

```bash
# On your local machine
cd face-registration
npm run build:production

cd ../Smart\ Building\ Dashboard\ Design
npm run build:production
```

**Copy build files to EC2:**
```bash
scp -r face-registration/dist ubuntu@35.180.227.44:/tmp/face-dist
scp -r "Smart Building Dashboard Design/dist" ubuntu@35.180.227.44:/tmp/dashboard-dist
```

**On EC2:**
```bash
sudo mv /tmp/face-dist /var/www/html/face-registration
sudo mv /tmp/dashboard-dist /var/www/html/dashboard
sudo chown -R www-data:www-data /var/www/html/face-registration
sudo chown -R www-data:www-data /var/www/html/dashboard
```

---

## 📊 Employee Photo Usage in Frontend

```typescript
// Fetch employees with photo URLs
const response = await fetch('http://35.180.227.44/api/v1/employees');
const data = await response.json();

// Display photos using photo_url
data.employees.forEach(employee => {
  if (employee.photo_url) {
    console.log(`Photo URL: ${employee.photo_url}`);
    // Use in <img src={employee.photo_url} />
  }
});

// OR get base64 for offline/caching
const photoResponse = await fetch(`http://35.180.227.44/api/v1/employees/${employeeId}/photo`);
const photoData = await photoResponse.json();

// Use data_url in img tag
// <img src={photoData.data_url} />
```

---

## 🛠️ Troubleshooting

### Permission Issues
```bash
sudo chown -R www-data:www-data /var/www/html/aegis-ignis
sudo chmod -R 775 /var/www/html/aegis-ignis/backend-laravel/storage
sudo chmod -R 775 /var/www/html/aegis-ignis/backend-laravel/bootstrap/cache
```

### Database Connection Issues
```bash
# Test PostgreSQL connection
sudo -u postgres psql -d aegis_ignis -U aegis_user -h 127.0.0.1
```

### Nginx Issues
```bash
sudo nginx -t
sudo systemctl restart nginx
```

### Clear Laravel Cache
```bash
cd /var/www/html/aegis-ignis/backend-laravel
sudo -u www-data php artisan cache:clear
sudo -u www-data php artisan config:clear
sudo -u www-data php artisan route:clear
sudo -u www-data php artisan view:clear
sudo -u www-data php artisan optimize
```

---

## ✅ Deployment Checklist

- [ ] EC2 instance accessible via SSH
- [ ] PHP 8.2 installed
- [ ] PostgreSQL installed and database created
- [ ] Redis installed and running
- [ ] Nginx installed and configured
- [ ] Repository cloned
- [ ] GitHub secrets configured (EC2_SSH_KEY, EC2_HOST, EC2_USER, DEPLOY_PATH)
- [ ] Laravel .env configured
- [ ] Laravel migrations run
- [ ] Storage linked
- [ ] Permissions set correctly
- [ ] Python services running locally via START-ALL.bat
- [ ] Frontend built and deployed
- [ ] API endpoints tested
- [ ] Employee photos accessible

---

## 🚀 Next Steps After Deployment

1. **Test all endpoints** using curl or Postman
2. **Check service logs** to ensure no errors
3. **Test frontend** by accessing http://35.180.227.44
4. **Monitor performance** using Laravel logs
5. **Setup SSL** (optional but recommended for production)
6. **Setup automated backups** for PostgreSQL database

---

**Your deployment workflow is ready! Push changes to `clean` branch and use GitHub Actions "Run workflow" button to deploy.**
