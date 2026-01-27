#!/bin/bash

# EC2 Cron Setup Script for Laravel Scheduler
# This script sets up the Laravel task scheduler to run automatically

APP_PATH="/var/www/aegis-ignis/Server"

# Detect the actual Laravel path if it exists
if [ -d "$APP_PATH" ]; then
    echo "Using Laravel path: $APP_PATH"
else
    # Try to find Laravel installation
    POSSIBLE_PATHS=(
        "/var/www/html/Server"
        "/home/ubuntu/aegis-ignis/Server"
        "$(pwd)/Server"
    )
    
    for path in "${POSSIBLE_PATHS[@]}"; do
        if [ -d "$path" ] && [ -f "$path/artisan" ]; then
            APP_PATH="$path"
            echo "Found Laravel at: $APP_PATH"
            break
        fi
    done
fi

if [ ! -f "$APP_PATH/artisan" ]; then
    echo "ERROR: Laravel installation not found at $APP_PATH"
    echo "Please update APP_PATH in this script with your actual Laravel path"
    exit 1
fi

# Backup existing crontab
echo "Backing up existing crontab..."
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || echo "No existing crontab to backup"

# Check if scheduler entry already exists
if crontab -l 2>/dev/null | grep -q "schedule:run"; then
    echo "Laravel scheduler entry already exists in crontab"
    echo "Current crontab:"
    crontab -l
    read -p "Do you want to replace it? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing scheduler entry
        crontab -l 2>/dev/null | grep -v "schedule:run" | crontab -
    else
        echo "Keeping existing entry. Exiting."
        exit 0
    fi
fi

# Add Laravel scheduler to crontab
echo "Adding Laravel scheduler to crontab..."
(crontab -l 2>/dev/null; echo "* * * * * cd $APP_PATH && php artisan schedule:run >> /dev/null 2>&1") | crontab -

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Cron setup complete!"
    echo ""
    echo "Current crontab:"
    crontab -l
    echo ""
    echo "Scheduled tasks:"
    echo "  - Alert Cleanup: Daily at 3:00 AM"
    echo "  - Alert Images Cleanup: Daily at 3:30 AM"
    echo "  - Photo Cleanup: Daily at 2:00 AM"
    echo ""
    echo "To test the scheduler, run:"
    echo "  cd $APP_PATH && php artisan schedule:run"
    echo ""
    echo "To view logs:"
    echo "  tail -f $APP_PATH/storage/logs/laravel.log"
else
    echo "ERROR: Failed to set up cron"
    exit 1
fi
