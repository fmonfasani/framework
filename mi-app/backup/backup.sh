#!/bin/bash

set -e

BACKUP_DIR="/tmp/backup/$(date +%Y%m%d_%H%M%S)"
mkdir -p $BACKUP_DIR

echo "Starting backup to $BACKUP_DIR"

# Database backup
docker-compose exec -T postgres pg_dump -U postgres postgres > $BACKUP_DIR/database.sql

# Application files backup
tar -czf $BACKUP_DIR/app_files.tar.gz .

echo "Backup completed: $BACKUP_DIR"
