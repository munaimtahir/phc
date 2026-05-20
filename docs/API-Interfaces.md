# API / Interfaces.md

This is primarily a Django template app. APIs are not required for MVP.

## URLs
Dashboard, health, login/logout, indicator list/detail, evidence list/add/detail/link, register list/detail/add-entry/print, reports, admin.

## Management Commands
```bash
python manage.py import_phc_indicators data/source_materials/test-export_framework_template_FIXED.csv
python manage.py bootstrap_evidence_requirements
python manage.py bootstrap_registers
python manage.py bootstrap_admin
```
