from django.contrib import admin
from .models import RegisterDefinition, RegisterEntry

@admin.register(RegisterDefinition)
class RegisterDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'frequency', 'active')
    search_fields = ('name', 'category')
    filter_horizontal = ('linked_indicators',)

@admin.register(RegisterEntry)
class RegisterEntryAdmin(admin.ModelAdmin):
    list_display = ('register_definition', 'entry_date', 'entered_by', 'verified_by')
    list_filter = ('register_definition', 'entry_date')
    date_hierarchy = 'entry_date'
