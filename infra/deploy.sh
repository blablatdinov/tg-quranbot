#!/bin/bash
set -euo pipefail

cd /home/www/code/tg-quranbot/infra

TAG_NAME=${TAG_NAME:-latest}
export TAG_NAME

echo "Starting deployment of version: ${TAG_NAME}"

docker compose -f docker-compose.prod.yml down --remove-orphans || true

docker compose -f docker-compose.prod.yml pull

docker compose -f docker-compose.prod.yml up -d --wait --wait-timeout 300

echo "Deployment completed successfully!"

docker compose -f docker-compose.prod.yml ps | grep -q "Up" || exit 1
