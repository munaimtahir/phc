from io import BytesIO
import json
from django.http import FileResponse
from rest_framework.views import APIView
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from apps.registry.models import Indicator
from apps.evidence.services import compliance_summary


class PrintPackView(APIView):
    def get(self, request):
        buffer = BytesIO()
        document = SimpleDocTemplate(buffer, pagesize=A4, title="PHC MSDS Compliance Print Pack")
        styles = getSampleStyleSheet()
        story = [Paragraph("PHC MSDS Compliance Print Pack", styles["Title"]),
                 Paragraph(f"Overall compliance: {compliance_summary()['compliance_percent']:.2f}%", styles["Heading2"]), Spacer(1, 12)]
        for number, indicator in enumerate(Indicator.objects.select_related("standard__domain").order_by("source_id"), 1):
            record = indicator.evidence_records.filter(is_current=True).order_by("-submitted_at", "-id").first()
            status = record.status if record else "no current evidence"
            evidence = (record.payload.get("content", "") if record and isinstance(record.payload, dict) else "")
            if record and not evidence:
                evidence = json.dumps(record.payload, ensure_ascii=False)
            story.extend([Paragraph(f"{number}. {indicator.standard.code} — {indicator.text}", styles["Heading3"]),
                          Paragraph(f"Weightage: {indicator.weightage} | Status: {status}", styles["BodyText"])])
            if evidence:
                story.append(Paragraph(evidence.replace("\n", "<br/>"), styles["BodyText"]))
            story.append(Spacer(1, 8))
        document.build(story)
        buffer.seek(0)
        return FileResponse(buffer, as_attachment=True, filename="phc-msds-print-pack.pdf", content_type="application/pdf")
