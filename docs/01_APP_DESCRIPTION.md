# App Description

PHC Lab Compliance Tracker is a Django-based inspection readiness system for Al Shifa Laboratory.

It converts the fixed PHC/MSDS Clinical / Pathology Laboratory checklist into:

- 118 locked indicators
- Evidence requirements for each indicator
- Evidence uploads and links
- Digital registers
- Recurring compliance tracking
- Score and readiness dashboard
- Printable surveyor evidence packs
- Safe local AI prompt generation

The application is intentionally single-purpose and practical. It is not a generic accreditation platform.

The key design principle is that one indicator may have multiple evidence requirements. Therefore, evidence is tracked at the evidence-requirement level and indicator readiness is calculated from evidence completion.
