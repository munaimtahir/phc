from django.contrib import admin
from .models import RegisterDefinition, RegisterEntry

@admin.register(RegisterDefinition)
class RegisterDefinitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'recurrence_mode', 'active')
    list_filter = ('recurrence_mode', 'active', 'category')
    search_fields = ('name',)

@admin.register(RegisterEntry)
class RegisterEntryAdmin(admin.ModelAdmin):
    list_display = ('register_definition', 'entry_date', 'entered_by', 'verified_by')
    list_filter = ('register_definition', 'entry_date')
