from django.contrib import admin
from .models import Indicator

@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ('indicator_no', 'standard_no', 'functional_area_code', 'indicator_text', 'max_score')
    list_filter = ('functional_area_code', 'standard_no', 'is_locked')
    search_fields = ('indicator_no', 'indicator_text', 'standard_title')
    readonly_fields = ('created_at', 'updated_at')
