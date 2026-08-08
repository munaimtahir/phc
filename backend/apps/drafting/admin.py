from django.contrib import admin
from .models import Draft


@admin.register(Draft)
class DraftAdmin(admin.ModelAdmin):
    list_display = ["id", "indicator_ids", "kind", "status", "version_no", "created_at"]
    list_filter = ["kind", "status"]
