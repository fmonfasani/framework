#!/bin/bash

set -e

echo "Starting deployment..."

# Build and deploy with docker-compose
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for services to be ready
echo "Waiting for services to start..."
sleep 30

# Health check
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "Backend health check passed"
else
    echo "Backend health check failed"
    exit 1
fi

if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "Frontend health check passed"
else
    echo "Frontend health check failed"
    exit 1
fi

echo "Deployment completed successfully!"
