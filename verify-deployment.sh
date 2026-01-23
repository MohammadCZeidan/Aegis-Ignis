#!/bin/bash
# Script to verify CD deployment is working

echo "=== Checking Docker Containers ==="
sudo docker ps

echo ""
echo "=== Checking Docker Compose Services ==="
cd /home/ubuntu/Aegis-IgnisGit || cd /var/www/html || cd $HOME/Aegis-IgnisGit
sudo docker compose -f docker-compose.prod.yml ps

echo ""
echo "=== Checking Container Logs (last 20 lines) ==="
sudo docker compose -f docker-compose.prod.yml logs --tail=20

echo ""
echo "=== Checking if Services are Accessible ==="
echo "Backend (port 8000):"
curl -I http://localhost:8000 || echo "Backend not responding"

echo ""
echo "Frontend (port 80):"
curl -I http://localhost:80 || echo "Frontend not responding"

echo ""
echo "=== Checking Disk Space ==="
df -h

echo ""
echo "=== Checking Docker Images ==="
sudo docker images | grep aegis

echo ""
echo "=== Deployment Verification Complete ==="
