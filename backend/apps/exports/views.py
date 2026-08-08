from django.http import HttpResponse
from rest_framework.decorators import api_view

from .services import generate_print_pack_pdf


@api_view(["GET"])
def print_pack_view(request):
    pdf_bytes = generate_print_pack_pdf()
    response = HttpResponse(pdf_bytes, content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="phc_msds_print_pack.pdf"'
    return response
