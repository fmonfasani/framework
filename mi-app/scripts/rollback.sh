#!/bin/bash

set -e

echo "Starting rollback..."

# Stop current deployment
docker-compose down

# Restore from backup (implement your backup strategy)
echo "Implement backup restoration logic here"

echo "Rollback completed!"
