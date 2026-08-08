import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.utils import ImageReader
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    Image,
    PageBreak,
)
from reportlab.lib import colors

from apps.registry.models import Indicator, LabProfile
from apps.compliance.services import compliance_snapshot

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}


def generate_print_pack_pdf() -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=1.5 * cm, bottomMargin=1.5 * cm)
    styles = getSampleStyleSheet()
    small = ParagraphStyle("small", parent=styles["Normal"], fontSize=9, leading=12)
    title_style = styles["Title"]
    heading_style = styles["Heading2"]

    profile = LabProfile.load()
    snapshot = compliance_snapshot()
    snapshot_by_id = {row["indicator"].id: row for row in snapshot["per_indicator"]}

    story = []
    story.append(Paragraph("PHC MSDS Compliance Print Pack", title_style))
    story.append(Paragraph(profile.lab_name, styles["Heading3"]))
    story.append(Paragraph(profile.address, small))
    story.append(Paragraph(f"PHC Registration No.: {profile.phc_registration_no}", small))
    story.append(Paragraph(f"Supervising Pathologist: {profile.supervising_pathologist}", small))
    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph(
        f"Overall compliance: {snapshot['overall_pct']:.2f}% "
        f"({snapshot['earned_total']:.1f} / {snapshot['possible_total']:.1f} weightage)",
        styles["Heading3"],
    ))
    story.append(Spacer(1, 0.5 * cm))

    indicators = Indicator.objects.select_related("standard", "standard__domain").order_by("id")

    current_domain = None
    for indicator in indicators:
        domain = indicator.standard.domain
        if domain.code != current_domain:
            current_domain = domain.code
            story.append(Spacer(1, 0.3 * cm))
            story.append(Paragraph(f"Domain {domain.code} — {domain.name}", heading_style))

        row = snapshot_by_id.get(indicator.id)
        status = row["status"] if row and row["status"] else "not_met"
        latest_record = row["latest_record"] if row else None

        header = f"#{indicator.id} [{indicator.standard.code}] {indicator.text} (weightage {indicator.weightage})"
        story.append(Paragraph(header, styles["Heading4"]))
        story.append(Paragraph(f"Status: {status.replace('_', ' ').title()}", small))

        if latest_record is None:
            story.append(Paragraph("No evidence submitted.", small))
        else:
            if latest_record.file:
                name = latest_record.file.name.lower()
                if any(name.endswith(ext) for ext in IMAGE_EXTENSIONS):
                    try:
                        img_reader = ImageReader(latest_record.file.path)
                        story.append(Image(img_reader, width=8 * cm, height=6 * cm, kind="proportional"))
                    except Exception:
                        story.append(Paragraph(f"Attached file: {latest_record.file.name}", small))
                else:
                    story.append(Paragraph(f"Attached file: {latest_record.file.name}", small))
            if latest_record.structured_data:
                for key, value in latest_record.structured_data.items():
                    if key == "content":
                        story.append(Paragraph(str(value)[:2000], small))
                    else:
                        story.append(Paragraph(f"{key}: {value}", small))
            if latest_record.period_label:
                story.append(Paragraph(f"Period: {latest_record.period_label}", small))

        story.append(Spacer(1, 0.3 * cm))

    doc.build(story)
    return buffer.getvalue()
