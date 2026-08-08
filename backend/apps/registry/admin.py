from django.contrib import admin

from .models import Domain, Standard, Indicator, LabProfile


@admin.register(Domain)
class DomainAdmin(admin.ModelAdmin):
    list_display = ["code", "name"]


@admin.register(Standard)
class StandardAdmin(admin.ModelAdmin):
    list_display = ["code", "domain", "title"]
    list_filter = ["domain"]


@admin.register(Indicator)
class IndicatorAdmin(admin.ModelAdmin):
    list_display = ["id", "standard", "category", "frequency", "evidence_format", "weightage"]
    list_filter = ["category", "frequency", "evidence_format"]
    search_fields = ["text"]


@admin.register(LabProfile)
class LabProfileAdmin(admin.ModelAdmin):
    list_display = ["lab_name", "phc_registration_no", "supervising_pathologist"]
