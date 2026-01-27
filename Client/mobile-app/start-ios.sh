#!/bin/bash

echo "Starting Aegis Ignis Mobile App for iOS..."
echo ""

cd "$(dirname "$0")"

echo "[1/2] Starting Metro bundler..."
osascript -e 'tell app "Terminal" to do script "cd \"'"$(pwd)"'\" && npm start"' &

sleep 5

echo "[2/2] Building and launching iOS app..."
npm run ios

echo ""
echo "App should launch on iOS simulator or connected device."
echo ""
