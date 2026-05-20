# Tests.md

## Core
- Health endpoint returns 200.
- Dashboard redirects if unauthenticated.
- Dashboard loads for authenticated user.

## Import
- Import command loads 118 indicators.
- Indicator numbers are unique.
- Evidence requirements are created.

## Evidence
- Evidence item can be created and uploaded.
- Evidence item can link to one or more requirements.
- Fulfillment status updates.

## Registers
- Register definition and entry can be created.
- Due/overdue logic works.
- Register entry can satisfy evidence requirement.

## Dashboard and Reports
- KPI cards calculate correctly.
- Missing evidence panel shows missing requirements.
- Score summary, evidence index, recurring report, and surveyor pack return 200.

## AI Prompt
- Prompt includes lab name, indicator number, evidence requirement, and approval/signature section.
- Prompt does not call live AI API.
