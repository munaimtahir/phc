#!/usr/bin/env bash
set -euo pipefail

SRC="/home/munaim/srv/proxy/caddy/Caddyfile"
DST="/etc/caddy/Caddyfile"
BACKUP="/etc/caddy/Caddyfile.backup.$(date +%Y%m%d_%H%M%S)"

echo "Backing up current system Caddyfile..."
sudo cp "$DST" "$BACKUP"

echo "Formatting source Caddyfile..."
# Try to run caddy fmt without sudo first, if fails use sudo
if ! caddy fmt --overwrite "$SRC" 2>/dev/null; then
    sudo caddy fmt --overwrite "$SRC"
fi

echo "Copying source Caddyfile to system Caddyfile..."
sudo cp "$SRC" "$DST"

echo "Validating Caddyfile..."
sudo caddy validate --config "$DST"

echo "Reloading Caddy..."
sudo systemctl reload caddy

echo "Done. Backup created at: $BACKUP"
