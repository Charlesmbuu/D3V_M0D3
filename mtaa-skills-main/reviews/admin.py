from django.contrib import admin
from .models import Review, ProviderStats

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['provider', 'reviewer', 'rating', 'created_at', 'is_verified']
    list_filter = ['rating', 'is_verified', 'created_at']
    search_fields = ['provider__business_name', 'reviewer__username', 'comment']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ProviderStats)
class ProviderStatsAdmin(admin.ModelAdmin):
    list_display = ['provider', 'average_rating', 'total_reviews', 'last_updated']
    readonly_fields = ['last_updated']
    list_filter = ['last_updated']
