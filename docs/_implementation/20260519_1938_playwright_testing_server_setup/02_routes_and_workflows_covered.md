# Routes and Workflows Covered

## Core Routes
- `/`
- `/indicators/`
- `/evidence/`
- `/registers/`
- `/reports/`
- `/accounts/login/`
- `/accounts/logout/` (via UI sign-out)
- optional probe for `/dashboard/` only if non-404

## Route Groups
- Indicators: list rendering, search/filter controls, detail navigation, status labels.
- Evidence: list/search UI, empty-state/table checks, optional create via admin.
- Registers: card/list checks, count sanity, add-entry flow (mutation-gated).
- Reports: report cards, missing evidence route, surveyor pack enabled/disabled behavior.
- Dashboard: status cards, summary labels, 118 total indicator expectation, section visibility.

## Layout Coverage
Desktop viewports:
- 1366x768
- 1440x900
- 1920x1080

Checks:
- sidebar visible
- main content visible
- main content x-position not overlapping sidebar width
- headings and first table/card visibility
