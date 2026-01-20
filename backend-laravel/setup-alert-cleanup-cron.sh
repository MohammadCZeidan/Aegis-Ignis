#!/bin/bash

# Alert Images Cleanup Setup for EC2
# This script sets up the Laravel scheduler cron job

echo "🔧 Setting up Alert Images Cleanup Cron Job..."

# Navigate to Laravel directory
cd /var/www/html/Aegis-Ignis/backend-laravel

# Test the cleanup command manually first
echo "Testing cleanup command..."
sudo -u www-data php artisan alerts:cleanup-images --help

# Add Laravel scheduler to crontab (if not already added)
CRON_CMD="* * * * * cd /var/www/html/Aegis-Ignis/backend-laravel && php artisan schedule:run >> /dev/null 2>&1"

# Check if cron job already exists
if ! sudo crontab -l -u www-data 2>/dev/null | grep -q "artisan schedule:run"; then
    echo "Adding Laravel scheduler to www-data crontab..."
    (sudo crontab -l -u www-data 2>/dev/null; echo "$CRON_CMD") | sudo crontab -u www-data -
    echo "✅ Cron job added successfully!"
else
    echo "✅ Cron job already exists"
fi

# Show current crontab
echo ""
echo "Current www-data crontab:"
sudo crontab -l -u www-data

# Test the scheduled tasks
echo ""
echo "Testing scheduled commands:"
sudo -u www-data php artisan schedule:list

echo ""
echo "✅ Setup complete!"
echo ""
echo "📋 The cleanup will run daily at 3:00 AM and delete alert images older than 1 day"
echo ""
echo "Manual commands:"
echo "  - Delete images older than 1 day:  php artisan alerts:cleanup-images --days=1"
echo "  - Delete ALL alert images:         php artisan alerts:cleanup-images --all"
echo "  - Test manual trigger from API:    POST http://35.180.227.44/api/v1/alerts/cleanup-images"
