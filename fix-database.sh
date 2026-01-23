#!/bin/bash
# Script to diagnose and fix database container issues

echo "=== Checking Database Container Logs ==="
sudo docker logs aegis-db --tail=50

echo ""
echo "=== Checking Database Container Status ==="
sudo docker ps -a | grep aegis-db

echo ""
echo "=== Checking Database Volume ==="
sudo docker volume ls | grep db_data

echo ""
echo "=== Attempting to Fix Database ==="
echo "Stopping database container..."
sudo docker stop aegis-db 2>/dev/null || true

echo "Removing database container..."
sudo docker rm aegis-db 2>/dev/null || true

echo "Checking if volume needs to be recreated..."
# Check volume permissions
sudo docker volume inspect db_data 2>/dev/null || echo "Volume doesn't exist, will be created"

echo ""
echo "Restarting database container..."
cd /home/ubuntu/Aegis-IgnisGit || cd /var/www/html || cd $HOME/Aegis-IgnisGit
sudo docker compose -f docker-compose.prod.yml up -d db

echo "Waiting for database to initialize (30 seconds)..."
sleep 30

echo ""
echo "=== Checking Database Status Again ==="
sudo docker ps | grep aegis-db

echo ""
echo "=== Database Logs After Restart ==="
sudo docker logs aegis-db --tail=20

echo ""
echo "=== If database is still restarting, check logs with: ==="
echo "sudo docker logs aegis-db"
