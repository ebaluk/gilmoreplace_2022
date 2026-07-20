#!/usr/bin/env bash
set -euo pipefail

DOMAIN="${1:-}"
EMAIL="${2:-}"

if [[ -z "$DOMAIN" || -z "$EMAIL" ]]; then
  echo "Usage: $0 <domain> <email>"
  exit 1
fi

cd "$(dirname "$0")/.."

echo "==> Starting nginx on :80 for ACME challenge..."
docker compose -f docker-compose.yml -f docker-compose.ssl.yml up -d nginx

echo "==> Requesting certificate for $DOMAIN..."
docker compose -f docker-compose.yml -f docker-compose.ssl.yml run --rm certbot \
  certonly --webroot -w /var/www/certbot \
  --email "$EMAIL" --agree-tos --no-eff-email \
  -d "$DOMAIN"

echo "==> Restarting nginx with SSL enabled..."
docker compose -f docker-compose.yml -f docker-compose.ssl.yml up -d nginx

echo "Done. Verify https://$DOMAIN/ and set up a cron/systemd timer for renew if desired."

