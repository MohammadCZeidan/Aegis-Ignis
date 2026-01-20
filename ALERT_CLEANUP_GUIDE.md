# Alert Images Cleanup System

## Overview
Automatically deletes alert images from both the database and filesystem to prevent storage buildup.

## Features
- **Daily Automatic Cleanup**: Runs every day at 3:00 AM
- **Manual Trigger**: API endpoint for on-demand cleanup
- **Configurable**: Delete images older than X days or all images
- **Safe**: Only deletes from alerts folder, preserves other images

## Setup on EC2

### 1. Upload the new files to EC2:
```bash
# From your local machine
scp -i "your-key.pem" backend-laravel/setup-alert-cleanup-cron.sh ubuntu@35.180.227.44:/tmp/

# SSH into EC2
ssh -i "your-key.pem" ubuntu@35.180.227.44

# Move and run setup script
sudo mv /tmp/setup-alert-cleanup-cron.sh /var/www/html/Aegis-Ignis/backend-laravel/
cd /var/www/html/Aegis-Ignis/backend-laravel
sudo chmod +x setup-alert-cleanup-cron.sh
sudo ./setup-alert-cleanup-cron.sh
```

### 2. Clear Laravel caches:
```bash
cd /var/www/html/Aegis-Ignis/backend-laravel
sudo -u www-data php artisan route:clear
sudo -u www-data php artisan config:clear
sudo -u www-data php artisan cache:clear
sudo -u www-data php artisan route:cache
```

## Manual Commands

### Run cleanup manually (on EC2):
```bash
cd /var/www/html/Aegis-Ignis/backend-laravel

# Delete images older than 1 day
sudo -u www-data php artisan alerts:cleanup-images --days=1

# Delete images older than 7 days
sudo -u www-data php artisan alerts:cleanup-images --days=7

# Delete ALL alert images
sudo -u www-data php artisan alerts:cleanup-images --all
```

## API Endpoint (Frontend Trigger)

### Endpoint: `POST /api/v1/alerts/cleanup-images`

**Request:**
```javascript
// Delete images older than 1 day (default)
fetch('http://35.180.227.44/api/v1/alerts/cleanup-images', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({
    days: 1  // Optional: number of days (default: 1)
  })
})

// Delete ALL alert images
fetch('http://35.180.227.44/api/v1/alerts/cleanup-images', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  body: JSON.stringify({
    all: true
  })
})
```

**Response:**
```json
{
  "success": true,
  "alerts_updated": 15,
  "files_deleted": 30,
  "message": "Cleanup completed: 15 alerts updated, 30 files deleted"
}
```

## Frontend Button Example

```tsx
// In your alerts component
const handleCleanupImages = async () => {
  if (!confirm('Delete all alert images? This cannot be undone.')) return;
  
  try {
    const response = await fetch('http://35.180.227.44/api/v1/alerts/cleanup-images', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
      },
      body: JSON.stringify({ all: true })
    });
    
    const result = await response.json();
    
    if (result.success) {
      alert(`Cleanup successful! ${result.files_deleted} files deleted`);
    } else {
      alert('Cleanup failed: ' + result.error);
    }
  } catch (error) {
    console.error('Cleanup error:', error);
    alert('Failed to cleanup images');
  }
};

// Button
<button onClick={handleCleanupImages} className="btn-danger">
  🗑️ Cleanup Alert Images
</button>
```

## Scheduled Tasks

The Laravel scheduler runs these tasks automatically:

| Task | Schedule | Description |
|------|----------|-------------|
| `photos:cleanup` | Daily 2:00 AM | Cleans up employee photos |
| `alerts:cleanup-images` | Daily 3:00 AM | Cleans up alert images (1 day old) |

### View scheduled tasks:
```bash
cd /var/www/html/Aegis-Ignis/backend-laravel
sudo -u www-data php artisan schedule:list
```

### View cron jobs:
```bash
sudo crontab -l -u www-data
```

## Troubleshooting

### Check if cron is running:
```bash
sudo systemctl status cron
```

### Check Laravel logs:
```bash
sudo tail -100 /var/www/html/Aegis-Ignis/backend-laravel/storage/logs/laravel.log
```

### Manually test the scheduler:
```bash
cd /var/www/html/Aegis-Ignis/backend-laravel
sudo -u www-data php artisan schedule:run
```

### Check storage permissions:
```bash
sudo chown -R www-data:www-data /var/www/html/Aegis-Ignis/backend-laravel/storage
sudo chmod -R 775 /var/www/html/Aegis-Ignis/backend-laravel/storage
```

## What Gets Deleted

1. **Database**: Sets `image` and `screenshot_path` fields to NULL in alerts table
2. **Filesystem**: Deletes image files from `storage/app/public/alerts/` directory
3. **Orphaned Files**: Removes any files in alerts folder not referenced in database

## Safety Features

- Only targets the `alerts` folder
- Configurable age threshold (default: 1 day)
- Logs all cleanup operations
- Does NOT delete alert records, only images
- Background execution prevents blocking
