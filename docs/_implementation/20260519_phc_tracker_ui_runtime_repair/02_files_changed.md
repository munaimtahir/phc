# 02 Files Changed

| File | Reason |
|---|---|
| `templates/indicators/indicator_list.html` | Fixed `endendfor` typo, improved search UI, linked IDs to detail. |
| `templates/base.html` | Fixed global layout (fixed sidebar width, margin-left for content), added active route highlighting, consolidated 'content' blocks. |
| `templates/core/dashboard.html` | Improved KPI card visibility, added High-Priority Missing Evidence table, improved Recently Updated info, added Quick Actions. |
| `templates/evidence/evidence_list.html` | Added visible search input, improved table columns, enhanced empty state. |
| `templates/registers/register_list.html` | Added search bar, added operational status to cards (total entries, last entry, due status). |
| `templates/reports/index.html` | Added live counts to cards, handled zero-ready state for print pack. |
| `templates/indicators/indicator_detail.html` | Improved status badges, added linked evidence items list. |
| `core/views.py` | Added `missing_indicators` context for dashboard. |
| `registers/views.py` | Added search filtering for registers. |
| `reports/views.py` | Added counts context for report index. |
| `config/settings.py` | Fixed environment variable mismatch (`DJANGO_DEBUG`, `DJANGO_SECRET_KEY`). |
