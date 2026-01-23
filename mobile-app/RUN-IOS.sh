#!/bin/bash

echo "Starting iOS app..."
echo ""

cd "$(dirname "$0")"

echo "Building and launching iOS app..."
echo "This may take 2-5 minutes on first build..."
echo ""

npm run ios

echo ""
echo "App should launch on iOS Simulator"
echo ""
