#!/bin/sh
# Post-build verification script to ensure React is bundled

echo "=== Verifying React is bundled ==="

# Check if dist directory exists
if [ ! -d "dist" ]; then
  echo "ERROR: dist directory not found!"
  exit 1
fi

# Check if index.html exists
if [ ! -f "dist/index.html" ]; then
  echo "ERROR: index.html not found!"
  exit 1
fi

# Check if any JS files exist
JS_FILES=$(find dist/assets -name "*.js" -type f 2>/dev/null | wc -l)
if [ "$JS_FILES" -eq 0 ]; then
  echo "ERROR: No JavaScript files found in dist/assets!"
  exit 1
fi

echo "Found $JS_FILES JavaScript file(s)"

# Check if React is referenced in the built files
REACT_FOUND=false
for js_file in dist/assets/*.js; do
  if [ -f "$js_file" ]; then
    # Check if file contains React-related code
    if grep -q "createContext\|React\|react-dom" "$js_file" 2>/dev/null; then
      REACT_FOUND=true
      echo "✓ React found in: $(basename $js_file)"
      break
    fi
  fi
done

if [ "$REACT_FOUND" = false ]; then
  echo "WARNING: React code not found in any JS files!"
  echo "Listing all JS files:"
  ls -lh dist/assets/*.js 2>/dev/null || echo "No JS files found"
else
  echo "✓ React is properly bundled!"
fi

echo "=== Build verification complete ==="
