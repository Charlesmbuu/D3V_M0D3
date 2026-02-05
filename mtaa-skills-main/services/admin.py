from django.contrib import admin
from .models import ServiceCategory, ServiceProvider

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'is_active']
    list_editable = ['is_active']
    search_fields = ['name']

admin.site.register(ServiceProvider)