# GitHub Actions Workflows

This directory contains CI/CD workflows for the Aegis-Ignis project.

## Workflows

### 1. 🚀 Deploy to EC2 (`deploy.yml`)
**Trigger**: Push to `main` or `master` branch, or manual trigger

Deploys all services to EC2:
- Laravel Backend
- Fire Detection Service
- Face Recognition Service
- Frontend Dashboard

**Required Secrets**:
- `EC2_SSH_KEY` - SSH private key for EC2 access
- `EC2_HOST` - EC2 instance IP or hostname
- `EC2_USER` - SSH username (default: ubuntu)
- `APP_PATH` - Application path on EC2 (default: /var/www/aegis-ignis)

### 2. 🧪 CI - Tests and Linting (`ci.yml`)
**Trigger**: Pull requests to `main`/`master`, pushes to `develop`/`staging`

Runs tests and linting for:
- Laravel Backend (PHPUnit tests)
- Python Services (flake8 linting)
- Frontend Dashboard (build validation)
- Security scanning (Trivy)

### 3. 🗑️ Reset Laravel Application (`reset-laravel.yml`)
**Trigger**: Manual trigger only (workflow_dispatch)

**⚠️ DESTRUCTIVE OPERATION** - Resets the Laravel application on EC2:
- Wipes and rebuilds database
- Deletes all storage files (alerts, detections, photos)
- Clears all caches
- Deletes all sessions

**Required Input**: Type "RESET" to confirm

**Options**:
- Delete database records
- Delete storage files
- Clear caches
- Delete sessions

## Setup Instructions

### 1. Configure GitHub Secrets

Go to your repository → Settings → Secrets and variables → Actions

Add the following secrets:

```
EC2_SSH_KEY=-----BEGIN RSA PRIVATE KEY-----
...
-----END RSA PRIVATE KEY-----

EC2_HOST=your-ec2-ip-or-hostname
EC2_USER=ubuntu
APP_PATH=/var/www/aegis-ignis
```

### 2. Generate SSH Key for EC2

On your local machine:
```bash
ssh-keygen -t rsa -b 4096 -f ~/.ssh/aegis-deploy -N ""
```

Add the public key to EC2:
```bash
ssh-copy-id -i ~/.ssh/aegis-deploy.pub ubuntu@your-ec2-ip
```

Copy the private key content to `EC2_SSH_KEY` secret:
```bash
cat ~/.ssh/aegis-deploy
```

### 3. EC2 Server Setup

Ensure your EC2 instance has:
- Git installed
- PHP 8.2 and Composer
- Python 3.10+
- Node.js 20+
- Nginx
- MySQL/MariaDB
- Proper directory permissions

### 4. Application Path Structure

```
/var/www/aegis-ignis/
├── backend-laravel/
├── fire-detection-service/
├── python-face-service/
└── Smart Building Dashboard Design/
```

## Usage

### Deploy to Production
```bash
# Automatic on push to main
git push origin main

# Or manually trigger
# Go to Actions → Deploy to EC2 → Run workflow
```

### Reset Application
```bash
# ⚠️ CAUTION: This will delete all data!
# Go to Actions → Reset Laravel Application → Run workflow
# Type "RESET" to confirm
# Select what to delete (database, storage, cache, sessions)
```

### Run CI Tests
```bash
# Automatic on pull requests
# Or push to develop/staging branches
git push origin develop
```

## Monitoring Deployments

- View deployment status in the Actions tab
- Check logs for each step
- Failed deployments will not affect running services
- Services restart automatically after successful deployment

## Troubleshooting

### SSH Connection Failed
- Verify `EC2_SSH_KEY` is correct
- Check EC2 security group allows SSH (port 22)
- Verify `EC2_HOST` and `EC2_USER` are correct

### Deployment Failed
- Check EC2 instance has enough disk space
- Verify all required services are installed
- Check file permissions on EC2
- Review deployment logs in Actions tab

### Reset Failed
- Ensure PHP-FPM and Nginx services exist
- Check database credentials in `.env`
- Verify storage directory permissions

## Best Practices

1. **Always test in staging first** before deploying to production
2. **Use reset workflow carefully** - it's destructive
3. **Monitor logs** after deployment
4. **Keep secrets secure** - never commit them to repository
5. **Test CI locally** before pushing to avoid failing builds

## Support

For issues or questions, check:
- GitHub Actions logs
- EC2 server logs: `/var/log/nginx/`, `/var/log/php8.2-fpm/`
- Application logs: `backend-laravel/storage/logs/`
