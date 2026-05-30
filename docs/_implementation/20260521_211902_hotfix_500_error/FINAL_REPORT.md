# Hotfix Report: 500 Server Error Resolution

## 1. Problem Summary
The user reported a 500 Server Error when accessing the application at `https://phc.alshifalab.pk`.

## 2. Root Cause Analysis
The error was caused by a database schema inconsistency. New columns added in the previous sprint (`physical_confirmed`, `display_confirmed`, `staff_awareness_confirmed`) were missing from the production `evidence_evidencerequirementfulfillment` table. This happened because migrations were regenerated and "faked" without properly updating the existing SQLite database columns.

## 3. Resolution Steps
1.  **Diagnosis**: Enabled Gunicorn access logs and simulated dashboard access via Django shell to identify the missing column traceback (`sqlite3.OperationalError: no such column`).
2.  **Migration Recovery**:
    *   Manually restored `evidence.0001_initial` migration to fix broken dependency chain in `registers` app.
    *   Regenerated `evidence.0002` migration to include the new fields and `IndicatorEvidenceProfile` model.
3.  **Database Fix**:
    *   Added missing columns (`physical_confirmed`, `display_confirmed`, `staff_awareness_confirmed`) to the production SQLite database via `ALTER TABLE` commands.
    *   Faked migration `0002` to bring Django migration state in sync with the database.
4.  **Verification**:
    *   Tested Dashboard view logic in shell (Returned HTTP 200).
    *   Verified public URL access to login page (Returned HTTP 200).
    *   Ran `seed_evidence_profiles --update` to ensure all production data is correctly populated.

## 4. Final Status: FIXED
Application is fully accessible at: https://phc.alshifalab.pk
Super admin credentials confirmed: `admin` / `admin123`.
