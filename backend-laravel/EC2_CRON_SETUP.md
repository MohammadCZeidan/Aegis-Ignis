# EC2 Cron Setup for Alert Cleanup

This guide explains how to set up automatic alert cleanup on your EC2 instance.

## Overview

The system has two cleanup commands:
1. **`alerts:cleanup`** - Deletes both database records AND files (recommended)
2. **`alerts:cleanup-images`** - Only deletes image files, keeps database records

## Laravel Scheduler Setup

Laravel's task scheduler runs the cleanup automatically, but you need to add a cron entry to trigger it.

### Step 1: SSH into your EC2 instance

```bash
ssh -i your-key.pem ubuntu@your-ec2-ip
```

### Step 2: Edit the crontab

```bash
crontab -e
```

### Step 3: Add Laravel Scheduler Entry

Add this line to run Laravel's scheduler every minute:

```cron
* * * * * cd /var/www/aegis-ignis/backend-laravel && php artisan schedule:run >> /dev/null 2>&1
```

**Important:** Replace `/var/www/aegis-ignis/backend-laravel` with your actual Laravel application path.

### Step 4: Verify the cron is running

Check if the cron job is active:

```bash
crontab -l
```

You should see the scheduler entry.

### Step 5: Test the scheduler

Run the scheduler manually to test:

```bash
cd /var/www/aegis-ignis/backend-laravel
php artisan schedule:run
```

Check the logs:

```bash
tail -f storage/logs/laravel.log
```

## Scheduled Tasks

The following tasks are configured in `app/Console/Kernel.php`:

1. **Alert Cleanup** - Daily at 3:00 AM
   - Deletes alerts older than 1 day
   - Removes both database records and files
   - Command: `alerts:cleanup --days=1`

2. **Alert Images Cleanup** - Daily at 3:30 AM (legacy)
   - Only deletes image files
   - Keeps database records
   - Command: `alerts:cleanup-images --days=1`

3. **Photo Cleanup** - Daily at 2:00 AM
   - Cleans up unused photos
   - Command: `photos:cleanup --force`

## Manual Cleanup (Button/API)

You can trigger cleanup manually via API:

### Delete alerts older than X days

```bash
POST /api/v1/alerts/cleanup
Content-Type: application/json

{
  "days": 1
}
```

### Delete ALL alerts

```bash
POST /api/v1/alerts/cleanup
Content-Type: application/json

{
  "all": true
}
```

### Delete only images (keep database records)

```bash
POST /api/v1/alerts/cleanup
Content-Type: application/json

{
  "days": 1,
  "images-only": true
}
```

## Troubleshooting

### Cron not running?

1. Check if cron service is running:
   ```bash
   sudo service cron status
   ```

2. Check cron logs:
   ```bash
   grep CRON /var/log/syslog
   ```

3. Verify the path in crontab is correct:
   ```bash
   cd /var/www/aegis-ignis/backend-laravel
   pwd  # Use this exact path in crontab
   ```

### Scheduler not executing tasks?

1. Check Laravel logs:
   ```bash
   tail -f storage/logs/laravel.log
   ```

2. Test a command manually:
   ```bash
   php artisan alerts:cleanup --days=1
   ```

3. Check file permissions:
   ```bash
   ls -la storage/logs/
   chmod -R 775 storage/
   ```

### Tasks running but not deleting?

1. Check database permissions
2. Check storage permissions:
   ```bash
   ls -la storage/app/public/alerts/
   chmod -R 775 storage/app/public/alerts/
   ```

3. Verify the Alert model and database structure

## Testing

### Test cleanup command manually

```bash
# Delete alerts older than 1 day
php artisan alerts:cleanup --days=1

# Delete all alerts
php artisan alerts:cleanup --all

# Delete only images
php artisan alerts:cleanup --days=1 --images-only
```

### Test via API (from your frontend or Postman)

```bash
curl -X POST http://your-ec2-ip/api/v1/alerts/cleanup \
  -H "Content-Type: application/json" \
  -H "Accept: application/json" \
  -d '{"days": 1}'
```

## Monitoring

Check cleanup logs:

```bash
# View recent cleanup logs
grep "Alert cleanup" storage/logs/laravel.log

# View all scheduler logs
grep "schedule" storage/logs/laravel.log
```

## Quick Setup Script

Save this as `setup-cron.sh` and run it on your EC2:

```bash
#!/bin/bash

APP_PATH="/var/www/aegis-ignis/backend-laravel"

# Add Laravel scheduler to crontab
(crontab -l 2>/dev/null; echo "* * * * * cd $APP_PATH && php artisan schedule:run >> /dev/null 2>&1") | crontab -

echo "Cron setup complete!"
echo "Current crontab:"
crontab -l
```

Make it executable and run:

```bash
chmod +x setup-cron.sh
./setup-cron.sh
```
