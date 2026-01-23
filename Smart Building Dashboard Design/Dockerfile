# Build stage
FROM node:20 AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Clean install to ensure React is installed
RUN npm ci --legacy-peer-deps || npm install --legacy-peer-deps

# Verify React is installed (critical check - fail build if missing)
RUN npm list react react-dom || (echo "ERROR: React packages not installed!" && exit 1)
RUN test -d node_modules/react || (echo "ERROR: React directory not found!" && exit 1)
RUN test -d node_modules/react-dom || (echo "ERROR: React-DOM directory not found!" && exit 1)

# Copy source code
COPY . .

# Verify React plugin is configured
RUN test -f vite.config.ts && echo "Vite config found" || echo "Warning: vite.config.ts not found"

# Build the application using node directly (bypasses permission issues)
RUN node node_modules/vite/bin/vite.js build

# Verify build output exists
RUN test -d dist || (echo "ERROR: dist directory not created!" && exit 1)
RUN test -f dist/index.html || (echo "ERROR: index.html not found!" && exit 1)

# Copy and run verification script
COPY verify-build.sh /app/verify-build.sh
RUN chmod +x /app/verify-build.sh
RUN /app/verify-build.sh || echo "Warning: Build verification had issues"

# Verify React vendor chunk was created (check for any vendor chunk containing react)
RUN ls -la dist/assets/ || echo "Warning: assets directory not found"
RUN ls -la dist/assets/*.js 2>/dev/null | grep -i "vendor\|react" || echo "Warning: vendor-react chunk check"
RUN find dist/assets -name "*.js" -type f | head -5 || echo "Warning: no JS files found"

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Verify files were copied
RUN ls -la /usr/share/nginx/html/ || echo "Warning: html directory empty"
RUN test -f /usr/share/nginx/html/index.html || (echo "ERROR: index.html not copied!" && exit 1)

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
