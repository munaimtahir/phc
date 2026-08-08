from django.urls import path

from .views import (
    due_list_view,
    structured_form_schema_view,
    evidence_history_view,
    submit_evidence_view,
)

urlpatterns = [
    path("due-list/", due_list_view, name="due-list"),
    path("submit/", submit_evidence_view, name="submit-evidence"),
    path("structured-form-schema/<int:indicator_id>/", structured_form_schema_view, name="structured-form-schema"),
    path("history/<int:indicator_id>/", evidence_history_view, name="evidence-history"),
]
