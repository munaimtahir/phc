# Architecture.md

## Architecture Type
Django monolith.

## Apps
core, accounts, indicators, evidence, registers, reports.

## Key Flow
PHC CSV → Indicator import → Evidence requirement bootstrap → Indicator detail checklist → Evidence upload/linking → Register entry creation → Status/scoring calculation → Dashboard/reports.

## Key Principle
Evidence is linked to EvidenceRequirement, not only to Indicator.
