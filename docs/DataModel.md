# DataModel.md

## Indicator
indicator_no, functional_area_code, functional_area_name, standard_no, standard_code, standard_title, indicator_text, compliance_requirement, surveyor_check, scoring_note, max_score, weightage_percent, partial_allowed, partial_score_percent, source_reference, is_locked.

## EvidenceRequirement
indicator, title, description, evidence_type, document_type, ai_generation_mode, recurrence_mode, recurrence_frequency, minimum_required_count, display_required, physical_verification_required, human_approval_required, upload_required, template_reusable, evidence_reuse_policy, sort_order, active.

## EvidenceItem
title, evidence_type, document_type, file, external_url, physical_file_location, display_location, evidence_date, version, document_code, effective_date, review_date, approval_status, approved_by, approved_at, description, uploaded_by, source_type, source_register_entry.

## EvidenceRequirementFulfillment
evidence_requirement, evidence_item, status, verified_by, verified_at, remarks.

## RegisterDefinition
name, category, linked_evidence_requirements, frequency, recurrence_mode, fields_schema, printable, active, description.

## RegisterEntry
register_definition, entry_date, values_json, entered_by, verified_by, verified_at, remarks.
