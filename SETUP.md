# Setup

Recommended server path:

```bash
mkdir -p /home/munaim/srv/apps
cd /home/munaim/srv/apps
git clone <your-repo-url> phc
cd phc
cp .env.example .env
docker compose up -d --build
```

Caddy block:

```caddy
phc.alshifalab.pk {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8018
}
```

Expected URL:

```text
https://phc.alshifalab.pk
```
