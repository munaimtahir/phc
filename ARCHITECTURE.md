# Architecture

Use a Django monolith:
- Django views/templates
- HTMX for light interactivity
- PostgreSQL database
- WeasyPrint for PDF exports
- local media storage initially
- Caddy reverse proxy for public HTTPS

Apps:
- core: dashboard and shared utilities
- accounts: simple authentication/profile
- indicators: PHC checklist master and compliance record
- evidence: evidence library and indicator evidence links
- registers: digital registers/logs and recurrence
- reports: printable packs and exports
