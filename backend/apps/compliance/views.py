from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services import compliance_snapshot


@api_view(["GET"])
def compliance_view(request):
    snap = compliance_snapshot()
    per_indicator = [
        {
            "indicator_id": row["indicator"].id,
            "status": row["status"],
            "earned_weightage": row["earned_weightage"],
            "possible_weightage": row["possible_weightage"],
        }
        for row in snap["per_indicator"]
    ]
    return Response({
        "overall_pct": round(snap["overall_pct"], 2),
        "earned_total": snap["earned_total"],
        "possible_total": snap["possible_total"],
        "per_indicator": per_indicator,
    })
