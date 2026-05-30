# Caddy Reverse Proxy Configuration

To expose the application securely on `phc.alshifalab.pk`, add the following block to your global Caddyfile:

```caddy
phc.alshifalab.pk {
    encode zstd gzip
    reverse_proxy 127.0.0.1:8018
}
```

Make sure the Docker Compose service is running and properly binding to host port 8018.
