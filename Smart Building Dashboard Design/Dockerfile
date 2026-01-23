# Build stage
FROM node:20 AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Verify React is installed (critical check)
RUN npm list react react-dom || (echo "ERROR: React packages not installed!" && exit 1)

# Copy source code
COPY . .

# Build the application using node directly (bypasses permission issues)
RUN node node_modules/vite/bin/vite.js build

# Verify React vendor chunk was created
RUN ls -la dist/assets/ | grep -i "vendor-react" || echo "Warning: vendor-react chunk not found"

# Production stage
FROM nginx:alpine

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
