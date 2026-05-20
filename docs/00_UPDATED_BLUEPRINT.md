# PHC Lab Compliance Tracker — Updated Blueprint

Version: 2.0  
Date: 2026-05-20  
Project folder: `/home/munaim/srv/apps/phc`  
Public URL: `https://phc.alshifalab.pk`  
Primary Lab: Al Shifa Laboratory, Circular Road, Jaranwala  
Lab Manager / In-charge: Dr. Muhammad Munaim Tahir  
Consultant Pathologist / Approving Authority: Dr. Mubasher Ahmed  

---

## 1. Executive Summary

PHC Lab Compliance Tracker is a single-purpose Django application for managing Punjab Healthcare Commission (PHC) MSDS compliance for one fixed Clinical / Pathology Laboratory checklist.

It is not a generic accreditation SaaS platform.

The central question of the application is:

> Are we ready for PHC Lab inspection, and where is the evidence?

The system converts the fixed PHC laboratory checklist into trackable indicators, evidence requirements, evidence files, digital registers, recurring records, scoring, and printable surveyor packs.

---

## 2. Core Design Decision

The system must not track evidence only at the indicator level.

Correct design:

```text
Indicator
  → Evidence Requirement
      → Evidence Item / Register Entry / Physical Proof
```

Reason:

One PHC indicator may require more than one evidence item.

Example:

```text
IND-007 Mission Statement
  1. Mission statement document
  2. Displayed mission statement
  3. Approval/signature evidence
  4. Optional photo of display
```

Therefore, readiness should be calculated from evidence requirement fulfillment, not from one manually selected indicator status alone.

---

## 3. Fixed PHC Framework

The application is built around one fixed PHC/MSDS Clinical / Pathology Laboratory framework:

- 37 standards
- 118 indicators
- 10 functional areas:
  - ROM: Responsibilities of Management
  - FMS: Facility Management and Safety
  - HRM: Human Resource Management
  - MER: Management of Equipment and Reagents
  - RRS: Recording and Reporting System
  - QA: Quality Assurance
  - BSBS: Bio Safety and Bio Security
  - AAC: Access, Assessment, and Continuity of Care
  - COP: Care of Patients
  - PRE: Patient Rights and Education

The indicator list is imported once, locked, and treated as master data.

---

## 4. Practical Goal

A non-technical lab manager should be able to:

1. See all 118 PHC indicators.
2. See what evidence is required for each indicator.
3. Upload or link evidence.
4. Maintain digital registers.
5. Track recurring compliance.
6. See missing or partial compliance.
7. View readiness score.
8. Print a surveyor-ready evidence index and pack.
9. Generate safe AI prompts for drafting documents externally.
10. Avoid overclaiming compliance when physical, signed, or real-world evidence is missing.

---

## 5. Core Modules

### 5.1 Dashboard

The dashboard is an action dashboard.

It shows:

- Total indicators
- Missing indicators
- Partial indicators
- Ready indicators
- Verified indicators
- Current PHC score
- Maximum possible score
- Readiness percentage
- Evidence requirement completion
- Uploaded evidence count
- Active digital registers
- Overdue registers
- Due-soon registers
- Functional area progress
- Standard-wise progress
- Missing evidence panel
- Overdue evidence/register panel
- Recently updated indicators

### 5.2 Indicators

Locked PHC checklist.

Each indicator stores:

- Indicator number
- Functional area
- Standard code
- Standard title
- Indicator text
- Compliance requirement
- Surveyor check
- Scoring note
- Max score
- Weightage
- Partial compliance rule
- Source reference
- Locked status

### 5.3 Evidence Requirements

This is the key new layer.

Each indicator can have one or more evidence requirements.

Examples:

- SOP document
- Policy document
- Register template
- Register entry
- Display notice
- Physical arrangement
- Photo evidence
- License/certificate
- MOU/contract
- Appointment order
- Staff training record
- Audit report
- Patient record proof
- LIMS/system screenshot

Each evidence requirement stores:

- Title
- Description
- Evidence type
- Document type
- AI generation mode
- Recurrence mode
- Frequency
- Minimum required count
- Whether display is required
- Whether human approval is required
- Whether upload is required
- Whether physical verification is required
- Whether template reuse is allowed

### 5.4 Evidence Library

Stores evidence items such as:

- PDF
- Word document
- Image/photo
- Register printout
- Certificate/license
- MOU/contract
- External URL
- Physical file reference
- System screenshot
- Register entry

One evidence item may satisfy more than one evidence requirement.

### 5.5 Digital Registers

Registers are maintained inside the app.

Examples:

- Temperature Log
- Equipment Logbook
- Equipment Maintenance Register
- Calibration Register
- Reagent Inventory
- Stock Register
- EQA Record
- IQA / Process Cycle Record
- Complaint Register
- Critical Result Register
- Fire Drill Register
- Training Register
- Waste Disposal Register
- Incident / Sentinel Event Register

Register entries should automatically become evidence where linked.

### 5.6 Reports

Reports include:

- PHC score summary
- Missing evidence report
- Evidence requirement report
- Evidence index
- Register compliance report
- Surveyor pack index
- Functional area readiness report
- Overdue recurring compliance report

### 5.7 AI Prompt Generator

Stage 1 AI design is prompt-only.

The app does not call live AI APIs.

The app generates prompts that the user can copy into ChatGPT/Gemini manually.

Prompt generation should be based on a selected evidence requirement, not only on the indicator.

Prompt types:

- SOP / Policy
- Register Template
- Display Notice
- Appointment Order
- Gap Action Plan
- Surveyor Explanation
- Evidence Checklist
- Training Material
- Compliance Summary

---

## 6. Evidence Type Vocabulary

Use these controlled values:

```text
CONTROLLED_DOCUMENT
DISPLAY_NOTICE
PHYSICAL_FACILITY
LICENSE_CERTIFICATE
CONTRACT_MOU
HR_DOCUMENT
HR_RECORD
TRAINING_RECORD
REGISTER_LOGBOOK
LIMS_SYSTEM_RECORD
AUDIT_QA_REPORT
INVENTORY_STOCK
PHOTO_EVIDENCE
SYSTEM_SCREENSHOT
MIXED_EVIDENCE
```

---

## 7. Document Type Vocabulary

Use these controlled values:

```text
SOP
POLICY
PROTOCOL
MISSION_STATEMENT
ORGANOGRAM
APPOINTMENT_ORDER
AUTHORIZATION_LETTER
JOB_DESCRIPTION
ELIGIBILITY_CRITERIA
CHECKLIST
REGISTER
LOGBOOK
INVENTORY
AUDIT_REPORT
MONITORING_REPORT
TRAINING_ATTENDANCE
DISPLAY_NOTICE
CERTIFICATE
LICENSE
MOU
CONTRACT
PHOTO_EVIDENCE
SYSTEM_SCREENSHOT
DECLARATION
OTHER
```

---

## 8. AI Generation Modes

Use these controlled values:

```text
AI_DRAFTABLE
AI_TEMPLATE_ONLY
AI_ASSISTED_REVIEW
HUMAN_UPLOAD_REQUIRED
PHYSICAL_IMPLEMENTATION_REQUIRED
HUMAN_APPROVAL_REQUIRED
NO_AI_NEEDED
```

Meaning:

| Mode | Meaning |
|---|---|
| AI_DRAFTABLE | AI can draft a full document such as SOP/policy |
| AI_TEMPLATE_ONLY | AI can create format; real data must be entered by staff |
| AI_ASSISTED_REVIEW | AI can help review gaps or summarize records |
| HUMAN_UPLOAD_REQUIRED | Actual external certificate/license/MOU/report required |
| PHYSICAL_IMPLEMENTATION_REQUIRED | Physical arrangement required; AI can only prepare checklist/poster |
| HUMAN_APPROVAL_REQUIRED | Document must be approved/signed |
| NO_AI_NEEDED | Purely physical/system evidence |

---

## 9. Recurrence Modes

Use these controlled values:

```text
STATIC_ONCE
SCHEDULED_RECURRING
EVENT_DRIVEN
PER_PATIENT
PER_TEST
PER_EQUIPMENT
PER_EMPLOYEE
PER_STOCK_ENTRY
NONE
```

Examples:

| Mode | Example |
|---|---|
| STATIC_ONCE | Mission statement, organogram, policy |
| SCHEDULED_RECURRING | Annual training, biannual audit |
| EVENT_DRIVEN | Complaint, incident, sentinel event, critical result |
| PER_PATIENT | Patient record, report access code |
| PER_TEST | Process cycle record |
| PER_EQUIPMENT | Equipment log sheet, emergency contact label |
| PER_EMPLOYEE | Personal file, JD, credential verification |
| PER_STOCK_ENTRY | Reagent inventory, stock register |

---

## 10. Status Logic

### Evidence Requirement Status

```text
MISSING
DRAFT
PENDING_REVIEW
PARTIAL
READY
VERIFIED
REJECTED
EXPIRED
NOT_APPLICABLE
```

### Indicator Status

Indicator status should be calculated from its evidence requirements.

| Indicator Status | Logic |
|---|---|
| Missing | All required evidence requirements are missing |
| Partial | Some required evidence requirements are fulfilled |
| Ready | All mandatory evidence requirements are ready, but not verified |
| Verified | All mandatory evidence requirements are verified |
| Not Applicable | Approved as not applicable with reason |

Manual override may exist, but system-suggested status should always be visible.

---

## 11. Scoring Logic

Each PHC indicator has:

- Max score, usually 10
- Weightage percent, usually 100% or 80%
- Partial allowed flag
- Partial score percent, usually 80 where PHC allows partial scoring

Suggested MVP logic:

```text
Missing = 0
Partial = partial_score_percent × max_score only if partial_allowed=True
Ready = max_score
Verified = max_score
Not applicable = excluded only with documented approval
```

Important rule:

> Do not give partial score unless the PHC scoring rule allows partial compliance for that indicator.

---

## 12. Dashboard Logic

The dashboard should calculate:

```text
Current score = sum of indicator current scores
Maximum score = sum of applicable indicator max scores
Readiness % = current score / maximum score × 100
```

Functional area and standard progress should be calculated using the same evidence requirement layer.

---

## 13. Indicator Detail Page

Each indicator detail page should show:

1. Indicator details card
2. PHC compliance requirement
3. Scoring note
4. Evidence requirements checklist
5. Linked evidence items
6. Related register entries
7. AI prompt generator per evidence requirement
8. Gap summary and next action
9. Readiness/status card
10. Verification panel
11. Surveyor-pack inclusion checkbox

---

## 14. Evidence Requirement Checklist UI

For each evidence requirement, show:

- Evidence title
- Evidence type
- Document type
- AI mode
- Recurrence mode
- Required count
- Current linked evidence count
- Status
- Buttons:
  - Add evidence
  - Link existing evidence
  - Add register entry
  - Generate prompt
  - Mark not applicable
  - Verify

---

## 15. Reports

### 15.1 Missing Evidence Report

Should list missing evidence requirements, not just missing indicators.

Columns:

- Indicator number
- Standard
- Evidence requirement
- Evidence type
- Required action
- Gap summary
- Next action
- Responsible person
- Priority

### 15.2 Surveyor Pack Index

Organize by:

- Functional area
- Standard
- Indicator
- Evidence requirement
- Evidence item
- Evidence location
- Status
- Remarks

### 15.3 Evidence Index

Columns:

- Evidence item title
- Evidence type
- Document type
- Linked indicators
- Linked evidence requirements
- File/link/location
- Approval status
- Display status
- Evidence date
- Review date

---

## 16. Technical Architecture

### Architecture Type

Django monolith.

### Backend

- Django
- Django ORM
- PostgreSQL production
- SQLite local testing
- Gunicorn
- Docker Compose

### Frontend

- Django templates
- Bootstrap
- Minimal JavaScript
- Optional HTMX later

### Storage

- Local media folder initially
- Persistent Docker volume or bind mount

### Reverse Proxy

- Caddy
- Public URL: `https://phc.alshifalab.pk`
- Caddy reverse proxy target: `127.0.0.1:8018`

---

## 17. Django Apps

```text
core
accounts
indicators
evidence
registers
reports
```

Optional later:

```text
documents
auditlog
```

---

## 18. Import Workflow

Expected commands:

```bash
python manage.py import_phc_indicators data/source_materials/test-export_framework_template_FIXED.csv
python manage.py bootstrap_evidence_requirements
python manage.py bootstrap_registers
python manage.py bootstrap_admin
```

Expected result:

```text
118 indicators imported
Evidence requirements created/updated
Register definitions created/updated
Admin user created or confirmed
```

---

## 19. Development Priorities

### Phase 1 — Foundation

- Create Django project
- Configure Docker/Postgres
- Add authentication
- Add health endpoint
- Add models
- Import 118 indicators
- Create evidence requirements layer
- Add basic admin

### Phase 2 — Core Tracker

- Dashboard
- Indicator list
- Indicator detail
- Evidence requirement checklist
- Status calculation
- Scoring logic

### Phase 3 — Evidence Library

- Upload evidence
- Link evidence to evidence requirements
- Physical file reference
- Evidence approval status
- Evidence review date
- Display/photo support

### Phase 4 — Registers

- Register definitions
- Register entries
- Recurrence calculations
- Auto-link register entries as evidence
- Printable register pages

### Phase 5 — Reports

- Score summary
- Missing evidence report
- Evidence index
- Recurring compliance report
- Surveyor pack index

### Phase 6 — AI Prompt Generator

- Prompt generator service
- Evidence-requirement-specific prompts
- Copy button
- Download `.txt`
- Safe disclaimers
- No live AI API

### Phase 7 — Polish and Deployment

- Print CSS
- Caddy deployment
- Docker health checks
- Backup guidance
- Final QA gate

---

## 20. What Not To Add Yet

Do not add:

- Multi-framework system
- Project/workspace abstraction
- CAPA board
- Live AI API
- Complex RBAC
- React/Next.js frontend
- Advanced charts
- Complex task management
- SaaS billing/multi-tenant features

---

## 21. Success Criteria

The system is successful when:

1. All 118 indicators are imported and visible.
2. Each indicator has evidence requirements.
3. Evidence can be uploaded or linked.
4. Register entries can satisfy evidence requirements.
5. Missing evidence report is requirement-level.
6. Dashboard score reflects actual evidence status.
7. Overdue recurring compliance is visible.
8. Surveyor pack index is printable.
9. AI prompts can be generated safely.
10. A non-technical lab manager can operate it.
