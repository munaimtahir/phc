# Caddy Public Deployment Report

Date (UTC): 2026-05-19

## Local App Health Result
- `docker compose ps` in `/home/munaim/srv/apps/phc` shows `phc-web-1` running and mapped `127.0.0.1:8018->8000/tcp`.
- `curl -I http://127.0.0.1:8018/health/` returned `HTTP/1.1 200 OK`.

## Caddy Source File Edited
- `/home/munaim/srv/proxy/caddy/Caddyfile`

## System Caddy File Used
- Active Caddy service runs with `/etc/caddy/Caddyfile` (confirmed from `systemctl status caddy` and process args).

## Old `phc.alshifalab.pk` Routing Found
- Active system file had:
- `reverse_proxy 127.0.0.1:18080 { ... }`

## Final `phc.alshifalab.pk` Block
```caddy
phc.alshifalab.pk {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8018
}
```

## Backups Created
- `/home/munaim/srv/proxy/caddy/Caddyfile.backup_20260519_105639`
- `/etc/caddy/Caddyfile.backup_20260519_105717`

## Validation Result
- `sudo caddy validate --config /etc/caddy/Caddyfile` returned `Valid configuration`.
- Warning only: formatting suggestion from `caddy fmt`.

## Reload Result
- `sudo systemctl reload caddy` succeeded.
- `systemctl status caddy` shows reload process success and service active.

## Public Curl Result
- `curl -I https://phc.alshifalab.pk` returned `HTTP/2 302` to `/accounts/login/?next=/` via `Caddy`.
- `curl -I https://phc.alshifalab.pk/health/` returned `HTTP/2 200` via `Caddy`.
- DNS check: `phc.alshifalab.pk -> 34.10.178.210`.
- HTTPS is active and served successfully.

## Remaining Issues
- None blocking. Public routing is functional and points to port `8018`.
