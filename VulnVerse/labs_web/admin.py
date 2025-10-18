from django.contrib import admin
from .models import LabTemplate, LabInstance

@admin.register(LabTemplate)
class LabTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'lab_type', 'difficulty', 'is_active', 'created_at')
    list_filter = ('lab_type', 'difficulty', 'is_active')
    search_fields = ('name', 'description')

@admin.register(LabInstance)
class LabInstanceAdmin(admin.ModelAdmin):
    list_display = ('template', 'user', 'status', 'created_at', 'started_at', 'stopped_at')
    list_filter = ('status', 'template__lab_type')
    search_fields = ('user__username', 'template__name')
    readonly_fields = ('instance_uuid', 'created_at', 'started_at', 'stopped_at')
