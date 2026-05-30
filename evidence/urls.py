from django.urls import path
from . import views

urlpatterns = [
    path('', views.evidence_list, name='evidence_list'),
    path('worklist/', views.evidence_worklist, name='evidence_worklist'),
    path('document-transfer/', views.document_transfer_center, name='document_transfer_center'),
    path('document-transfer/export/all-docx.zip', views.export_all_generated_docx_zip, name='export_all_generated_docx_zip'),
    path('document-transfer/export/batch/<int:batch_id>.zip', views.export_batch_generated_docx_zip, name='export_batch_generated_docx_zip'),
    path('document-transfer/export/selected-docx.zip', views.export_selected_generated_docx_zip, name='export_selected_generated_docx_zip'),
    path('document-transfer/export/manifest.csv', views.export_document_transfer_manifest_csv, name='export_document_transfer_manifest_csv'),
    path('batches/', views.batch_list, name='batch_list'),
    path('batches/<int:pk>/', views.batch_detail, name='batch_detail'),
    path('planned-documents/<int:pk>/', views.planned_doc_detail, name='planned_document_detail'),
    path('generated-documents/', views.generated_doc_list, name='generated_document_list'),
    path('generated-documents/<int:pk>/', views.generated_doc_detail, name='generated_document_detail'),
    path('generated-documents/<int:pk>/download-docx/', views.download_docx, name='download_docx'),
    path('generated-documents/<int:pk>/upload-signed/', views.upload_signed_document, name='upload_signed_document'),
    path('add/', views.evidence_add, name='evidence_add'),
    path('<int:pk>/', views.evidence_detail, name='evidence_detail'),
    path('<int:pk>/link/', views.evidence_link, name='evidence_link'),
]
