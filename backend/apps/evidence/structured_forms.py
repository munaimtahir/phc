"""Field schemas for evidence_format=structured_form indicators.

PARKED: see docs/status/PARKED_DECISIONS.md #1 — the source
compliance_requirements text for indicators 6, 44, 46 and 50 does not spell out
an exact field set (unlike #53, which explicitly lists its fields). The field
sets below are a best-effort stub derived from each indicator's requirement
text, not an invented business rule about scoring/dates/etc. Confirm against
the lab's actual paper registers before relying on these in production.
"""

STRUCTURED_FORM_SCHEMAS: dict[int, list[dict]] = {
    6: [
        {"name": "date", "label": "Date", "type": "date", "required": True},
        {"name": "hours_present", "label": "Hours pathologist present", "type": "number", "required": True},
        {"name": "initials", "label": "Initials", "type": "text", "required": True},
    ],
    44: [
        {"name": "date", "label": "Date", "type": "date", "required": True},
        {"name": "item_name", "label": "Item", "type": "text", "required": True},
        {"name": "quantity_received", "label": "Quantity received", "type": "number", "required": False},
        {"name": "quantity_issued", "label": "Quantity issued", "type": "number", "required": False},
        {"name": "remarks", "label": "Remarks", "type": "text", "required": False},
    ],
    46: [
        {"name": "date", "label": "Date", "type": "date", "required": True},
        {"name": "reagent_name", "label": "Reagent", "type": "text", "required": True},
        {"name": "quantity_in_stock", "label": "Quantity in stock", "type": "number", "required": True},
        {"name": "expiry_date", "label": "Expiry date", "type": "date", "required": False},
    ],
    50: [
        {"name": "equipment_name", "label": "Equipment", "type": "text", "required": True},
        {"name": "date", "label": "Date", "type": "date", "required": True},
        {"name": "activity_type", "label": "Type", "type": "select", "options": ["breakdown", "repair", "maintenance", "calibration"], "required": True},
        {"name": "description", "label": "Description", "type": "text", "required": True},
        {"name": "performed_by", "label": "Performed by", "type": "text", "required": True},
    ],
    53: [
        {"name": "equipment_name", "label": "Equipment", "type": "text", "required": True},
        {"name": "date_of_purchase", "label": "Date of purchase", "type": "date", "required": True},
        {"name": "source", "label": "Source (manufacturer/importer/distributor/vendor)", "type": "text", "required": True},
        {"name": "date_of_commissioning", "label": "Date of commissioning", "type": "date", "required": True},
        {"name": "calibration_dates", "label": "Calibration date(s)", "type": "text", "required": False},
    ],
}


def schema_for(indicator_id: int) -> list[dict]:
    return STRUCTURED_FORM_SCHEMAS.get(indicator_id, [])
