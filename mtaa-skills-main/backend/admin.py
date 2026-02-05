from django.contrib import admin
from .models import *

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_user_type', 'phone_number', 'created_at']  # REMOVE 'role'
    list_filter = ['user__user_type', 'created_at']  # CHANGE 'role' to 'user__user_type'
    search_fields = ['user__username', 'user__email', 'phone_number']
    
    # Add this method to display user_type from the custom User model
    def get_user_type(self, obj):
        return obj.user.user_type
    get_user_type.short_description = 'Role'  # Set the column header

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'icon']

@admin.register(ServiceProvider)
class ServiceProviderAdmin(admin.ModelAdmin):
    list_display = ['business_name', 'user', 'location', 'is_verified', 'average_rating']
    list_filter = ['is_verified', 'categories']
    search_fields = ['business_name', 'user__username']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'customer', 'provider', 'status', 'budget', 'created_at']
    list_filter = ['status', 'category']
    search_fields = ['title', 'customer__username']

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'provider', 'proposed_amount', 'is_accepted', 'applied_at']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['job', 'amount', 'mpesa_number', 'status', 'created_at']

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['job', 'provider', 'customer', 'rating', 'created_at']

@admin.register(ProviderWallet)
class ProviderWalletAdmin(admin.ModelAdmin):
    list_display = ['provider', 'balance', 'total_earnings', 'last_updated']
    list_editable = ['balance', 'total_earnings']  # Make these editable in list view
    search_fields = ['provider__business_name', 'provider__user__username']
    list_filter = ['last_updated']
    
    # Add action to reset balances
    actions = ['reset_balances']
    
    def reset_balances(self, request, queryset):
        updated = queryset.update(balance=0)
        self.message_user(request, f'{updated} wallet balances reset to zero.')
    reset_balances.short_description = "Reset selected wallet balances to zero"