from __future__ import annotations

from decimal import Decimal

LAB_NAME = "Al Shifa Laboratory"
LAB_MANAGER = "Dr. Muhammad Munaim Tahir"
CONSULTANT_PATHOLOGIST = "Dr. Mubasher Ahmed"
NOT_SPECIFIED = "Not specified in tracker."

PROMPT_TYPE_SOP_POLICY = "sop_policy"
PROMPT_TYPE_REGISTER = "register_template"
PROMPT_TYPE_DISPLAY_NOTICE = "display_notice"
PROMPT_TYPE_GAP_ACTION_PLAN = "gap_action_plan"
PROMPT_TYPE_SURVEYOR_EXPLANATION = "surveyor_explanation"
PROMPT_TYPE_EVIDENCE_CHECKLIST = "evidence_checklist"
PROMPT_TYPE_TRAINING_MATERIAL = "training_material"
PROMPT_TYPE_COMPLIANCE_SUMMARY = "compliance_summary"

PROMPT_TYPES = [
    (PROMPT_TYPE_SOP_POLICY, "SOP / Policy"),
    (PROMPT_TYPE_REGISTER, "Register Template"),
    (PROMPT_TYPE_DISPLAY_NOTICE, "Display Notice"),
    (PROMPT_TYPE_GAP_ACTION_PLAN, "Gap Action Plan"),
    (PROMPT_TYPE_SURVEYOR_EXPLANATION, "Surveyor Explanation"),
    (PROMPT_TYPE_EVIDENCE_CHECKLIST, "Evidence Checklist"),
    (PROMPT_TYPE_TRAINING_MATERIAL, "Training Material"),
    (PROMPT_TYPE_COMPLIANCE_SUMMARY, "Compliance Summary"),
]


def _value_or_default(value: object) -> str:
    if value is None:
        return NOT_SPECIFIED
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, Decimal):
        value = str(value)
    text = str(value).strip()
    return text if text else NOT_SPECIFIED


def _functional_area(indicator) -> str:
    parts = [
        (indicator.functional_area_code or "").strip(),
        (indicator.functional_area_name or "").strip(),
    ]
    joined = " - ".join([p for p in parts if p])
    return joined or NOT_SPECIFIED


def _standard(indicator) -> str:
    code = (indicator.standard_code or "").strip()
    title = (indicator.standard_title or "").strip()
    if code and title:
        return f"{code} - {title}"
    if code:
        return code
    if title:
        return title
    return NOT_SPECIFIED


def get_prompt_context(indicator) -> dict[str, str]:
    compliance = getattr(indicator, "compliance", None)
    status_display = compliance.get_evidence_status_display() if compliance else None

    return {
        "lab_name": LAB_NAME,
        "lab_manager": LAB_MANAGER,
        "consultant_pathologist": CONSULTANT_PATHOLOGIST,
        "indicator_no": _value_or_default(indicator.indicator_no),
        "functional_area": _functional_area(indicator),
        "standard": _standard(indicator),
        "standard_code": _value_or_default(indicator.standard_code),
        "standard_title": _value_or_default(indicator.standard_title),
        "indicator_text": _value_or_default(indicator.indicator_text),
        "max_score": _value_or_default(indicator.max_score),
        "weightage": _value_or_default(indicator.weightage_percent),
        "compliance_requirement": _value_or_default(indicator.compliance_requirement),
        "surveyor_check": _value_or_default(indicator.surveyor_check),
        "required_evidence": _value_or_default(indicator.required_evidence),
        "evidence_category": _value_or_default(indicator.evidence_category),
        "register_required": _value_or_default(indicator.register_required),
        "register_name": _value_or_default(indicator.register_name),
        "recurring_required": _value_or_default(indicator.recurring_required),
        "recurrence_frequency": _value_or_default(indicator.recurrence_frequency),
        "physical_action_required": _value_or_default(indicator.physical_action_required),
        "evidence_status": _value_or_default(status_display),
        "gap_summary": _value_or_default(compliance.gap_summary if compliance else None),
        "next_action": _value_or_default(compliance.next_action if compliance else None),
        "evidence_location": _value_or_default(compliance.evidence_location if compliance else None),
    }


def render_prompt_template(prompt_type: str, context: dict[str, str]) -> str:
    template_map = {
        PROMPT_TYPE_SOP_POLICY: """Create a PHC/MSDS Clinical Laboratory compliant SOP or policy document for the following indicator.

Laboratory:
{lab_name}

Lab Manager / In-charge:
{lab_manager}

Consultant Pathologist:
{consultant_pathologist}

Indicator details:
- Indicator number: {indicator_no}
- Functional area: {functional_area}
- Standard: {standard}
- Indicator text: {indicator_text}
- Compliance requirement: {compliance_requirement}
- Surveyor check: {surveyor_check}
- Required evidence: {required_evidence}
- Current gap: {gap_summary}
- Next action: {next_action}

Write a practical inspection-ready SOP/policy in simple formal English for a small clinical/pathology laboratory in Punjab.

Use this structure:
1. Document title
2. Purpose
3. Scope
4. Policy statement
5. Roles and responsibilities
6. Procedure
7. Records/registers to maintain
8. Monitoring and review
9. Related PHC indicator
10. Approval section

Approval section should include:
- Prepared by: Dr. Muhammad Munaim Tahir, Lab Manager / In-charge
- Reviewed/Approved by: Dr. Mubasher Ahmed, Consultant Pathologist
- Effective date
- Review date
- Signature

Keep it concise, practical, and suitable for printing.

Do not mention that the document was generated by AI.""",
        PROMPT_TYPE_REGISTER: """Create a PHC/MSDS Clinical Laboratory compliant digital and printable register format for the following indicator.

Laboratory:
{lab_name}

Lab Manager / In-charge:
{lab_manager}

Consultant Pathologist:
{consultant_pathologist}

Indicator details:
- Indicator number: {indicator_no}
- Functional area: {functional_area}
- Standard: {standard}
- Indicator text: {indicator_text}
- Register required: {register_required}
- Register name: {register_name}
- Recurring required: {recurring_required}
- Frequency: {recurrence_frequency}
- Compliance requirement: {compliance_requirement}
- Required evidence: {required_evidence}

Create:
1. Register title
2. Purpose
3. Responsible person
4. Frequency of entry
5. Required columns
6. Verification/signature section
7. One sample filled row
8. Print-friendly table format
9. Related PHC indicator reference

Keep it simple enough for routine lab staff to fill.

Include approval footer:
Prepared by: Dr. Muhammad Munaim Tahir
Approved by: Dr. Mubasher Ahmed

Do not mention AI.""",
        PROMPT_TYPE_DISPLAY_NOTICE: """Create a short wall-display notice/poster text for PHC/MSDS Clinical Laboratory compliance.

Laboratory:
{lab_name}

Relevant PHC indicator:
- Indicator number: {indicator_no}
- Standard: {standard}
- Indicator text: {indicator_text}
- Required evidence: {required_evidence}
- Physical action required: {physical_action_required}

Requirements:
- Simple English
- Clear heading
- 5 to 8 short points
- Suitable for wall display in a clinical laboratory
- Professional but easy for patients/staff to understand
- Include footer: Al Shifa Laboratory
- Add "For assistance, contact the reception/lab staff."

Do not make it too long.
Do not mention AI.""",
        PROMPT_TYPE_GAP_ACTION_PLAN: """Create a practical gap closure action plan for PHC/MSDS Clinical Laboratory compliance.

Laboratory:
{lab_name}

Lab Manager / In-charge:
{lab_manager}

Consultant Pathologist:
{consultant_pathologist}

Indicator details:
- Indicator number: {indicator_no}
- Functional area: {functional_area}
- Standard: {standard}
- Indicator text: {indicator_text}
- Compliance requirement: {compliance_requirement}
- Required evidence: {required_evidence}
- Current evidence status: {evidence_status}
- Current gap: {gap_summary}
- Next action already noted: {next_action}

Create an action plan with:
1. What is missing
2. Why it matters for PHC inspection
3. Exact documents/evidence to prepare
4. Physical actions required, if any
5. Responsible person
6. Suggested deadline
7. Verification method
8. Final evidence file name suggestion

Keep it practical for immediate implementation in a small laboratory.

Do not mention AI.""",
        PROMPT_TYPE_SURVEYOR_EXPLANATION: """Create a short surveyor-facing compliance explanation for the following PHC/MSDS Clinical Laboratory indicator.

Laboratory:
{lab_name}

Indicator details:
- Indicator number: {indicator_no}
- Functional area: {functional_area}
- Standard: {standard}
- Indicator text: {indicator_text}
- Compliance requirement: {compliance_requirement}
- Required evidence: {required_evidence}
- Available evidence/status: {evidence_status}
- Evidence location: {evidence_location}
- Gap/remarks: {gap_summary}

Write:
1. A concise compliance statement
2. Evidence available for verification
3. Where the evidence is kept
4. Responsible person
5. Any pending improvement, if applicable

Tone:
Formal, honest, inspection-ready.

Do not overclaim compliance if evidence is partial or missing.
Do not mention AI.""",
        PROMPT_TYPE_EVIDENCE_CHECKLIST: """Create an evidence checklist for PHC/MSDS Clinical Laboratory inspection.

Laboratory:
{lab_name}

Indicator details:
- Indicator number: {indicator_no}
- Functional area: {functional_area}
- Standard: {standard}
- Indicator text: {indicator_text}
- Compliance requirement: {compliance_requirement}
- Surveyor check: {surveyor_check}
- Required evidence: {required_evidence}
- Evidence category: {evidence_category}
- Register required: {register_required}
- Register name: {register_name}
- Recurring required: {recurring_required}
- Frequency: {recurrence_frequency}

Create a checklist table with columns:
- Evidence item
- Type
- Required yes/no
- Available yes/no
- Location/file name
- Responsible person
- Remarks

Also provide:
1. Minimum evidence needed for inspection
2. Ideal evidence pack
3. Suggested file naming format

Keep it practical and concise.

Do not mention AI.""",
        PROMPT_TYPE_TRAINING_MATERIAL: """Create short staff training material for PHC/MSDS Clinical Laboratory compliance.

Laboratory:
{lab_name}

Topic based on PHC indicator:
- Indicator number: {indicator_no}
- Functional area: {functional_area}
- Standard: {standard}
- Indicator text: {indicator_text}
- Compliance requirement: {compliance_requirement}
- Required evidence: {required_evidence}

Create:
1. Training title
2. Learning objectives
3. Key points for staff
4. Step-by-step procedure
5. Common mistakes to avoid
6. Attendance record format
7. Short post-training questions
8. Trainer and approval section

Approval section:
Prepared by: Dr. Muhammad Munaim Tahir
Approved by: Dr. Mubasher Ahmed

Keep it suitable for laboratory staff and easy to deliver in 10–15 minutes.

Do not mention AI.""",
        PROMPT_TYPE_COMPLIANCE_SUMMARY: """Create a simple compliance summary for this PHC/MSDS Clinical Laboratory indicator.

Laboratory:
{lab_name}

Indicator details:
- Indicator number: {indicator_no}
- Functional area: {functional_area}
- Standard: {standard}
- Indicator text: {indicator_text}
- Compliance requirement: {compliance_requirement}
- Required evidence: {required_evidence}
- Current evidence status: {evidence_status}
- Gap summary: {gap_summary}
- Evidence location: {evidence_location}

Create:
1. What this indicator means
2. What PHC surveyor will check
3. What evidence should be available
4. Current status
5. What still needs to be done
6. Suggested final file name

Use simple English.
Do not mention AI.""",
    }
    if prompt_type not in template_map:
        prompt_type = PROMPT_TYPE_SOP_POLICY
    return template_map[prompt_type].format(**context)


def build_prompt(indicator, prompt_type: str) -> str:
    context = get_prompt_context(indicator)
    return render_prompt_template(prompt_type, context)
