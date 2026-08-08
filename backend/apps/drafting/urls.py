from django.urls import path
from .views import DraftListCreateView, DraftApproveView, BulkDraftView, ApprovedTemplateView

urlpatterns = [path("drafts/", DraftListCreateView.as_view()), path("drafts/bulk/", BulkDraftView.as_view()),
               path("drafts/<int:pk>/approve/", DraftApproveView.as_view()), path("templates/<int:indicator_id>/", ApprovedTemplateView.as_view())]
