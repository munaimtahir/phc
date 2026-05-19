#!/bin/bash

# Configuration
CADDY_FILE="/home/munaim/srv/proxy/caddy/Caddyfile"
PHC_BLOCK="phc.alshifalab.pk {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8018
}"

echo "Checking Caddy configuration..."

if [ ! -f "$CADDY_FILE" ]; then
    echo "Error: Caddyfile not found at $CADDY_FILE"
    exit 1
fi

# Check if the domain already exists
if grep -q "phc.alshifalab.pk" "$CADDY_FILE"; then
    echo "Domain phc.alshifalab.pk already exists in Caddyfile."
    echo "Updating port to 8018 if necessary..."
    # This is a simple replacement for the reverse_proxy line within that block context
    # Note: This assumes a standard format.
    sed -i '/phc.alshifalab.pk/,/}/ s/reverse_proxy .*/reverse_proxy 127.0.0.1:8018/' "$CADDY_FILE"
else
    echo "Adding new block for phc.alshifalab.pk..."
    echo -e "\n$PHC_BLOCK" >> "$CADDY_FILE"
fi

echo "Validating and Reloading Caddy..."

# Attempt reload via Docker if proxy is containerized
if [ -d "/home/munaim/srv/proxy/caddy" ] && [ -f "/home/munaim/srv/proxy/caddy/docker-compose.yml" ]; then
    cd /home/munaim/srv/proxy/caddy
    docker compose exec -t caddy caddy reload --config /etc/caddy/Caddyfile
else
    # Fallback to system caddy
    sudo caddy reload --config /etc/caddy/Caddyfile
fi

echo "Done! Please check https://phc.alshifalab.pk"
