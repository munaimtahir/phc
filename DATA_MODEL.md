# Data Model

## Indicator
Locked PHC indicator record.

Fields:
- indicator_no
- functional_area_code
- functional_area_name
- standard_no
- standard_code
- standard_title
- indicator_text
- max_score
- weightage_percent
- compliance_requirement
- surveyor_check
- required_evidence
- evidence_category
- register_required
- register_name
- recurring_required
- recurrence_frequency
- is_locked

## IndicatorCompliance
Working state for each indicator.

Fields:
- indicator
- evidence_status: missing/partial/ready/verified
- current_score
- gap_summary
- next_action
- evidence_location
- ready_for_print_pack
- notes
- updated_by
- updated_at

## EvidenceItem
Uploaded or linked evidence.

Fields:
- title
- evidence_type
- file
- external_url
- evidence_date
- linked_indicators
- description
- uploaded_by
- created_at

## RegisterDefinition
Digital register template.

Fields:
- name
- category
- linked_indicators
- frequency
- fields_schema
- printable
- active

## RegisterEntry
Single digital register entry.

Fields:
- register_definition
- entry_date
- values_json
- entered_by
- verified_by
- verified_at
- remarks
