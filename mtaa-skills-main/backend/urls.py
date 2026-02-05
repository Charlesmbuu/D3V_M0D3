from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

# Simple logout view
def custom_logout(request):
    logout(request)
    return redirect('home')

urlpatterns = [
    # ===== ADMIN =====
    path('admin/', admin.site.urls),
    #path('jet/', include('jet.urls', 'jet')),
    

    # ===== AUTHENTICATION =====
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    #path('accounts/logout/', views.logout_view, name='auth_logout'),
    
    # ===== PROFILE & SETTINGS =====
    path('profile/', views.profile, name='profile'),
    
    # ===== CUSTOMER URLs =====
    path('browse-providers/', views.browse_providers, name='browse_providers'),
    path('provider/<int:provider_id>/', views.provider_detail, name='provider_detail'),
    path('post-job/', views.post_job, name='post_job'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('customer-jobs/', views.customer_jobs, name='customer_jobs'),
    
    # ===== PROVIDER URLs =====
    path('provider-profile/', views.provider_profile, name='provider_profile'),
    path('available-jobs/', views.available_jobs, name='available_jobs'),
    path('job/<int:job_id>/apply/', views.apply_job, name='apply_job'),
    path('provider-jobs/', views.provider_jobs, name='provider_jobs'),
    path('provider-wallet/', views.provider_wallet, name='provider_wallet'),
    
    # ===== JOB MANAGEMENT (Both Customer & Provider) =====
    path('my-jobs/', views.redirect_my_jobs, name='redirect_my_jobs'),

    # ===== CHAT FUNCTIONALITY =====
    path('job/<int:job_id>/chat/', views.job_chat, name='job_chat'),
    
    # ===== COMPATIBILITY & REDIRECTS =====
    path('find-jobs/', views.find_jobs, name='find_jobs'),
    
    # ===== ADD THESE TWO LINES TO FIX BOTH URL PATTERNS =====
    path('my-jobs/', views.redirect_my_jobs, name='my_jobs'),  # For templates using 'my_jobs'
    
    # ===== DJANGO AUTH =====
    path('accounts/', include('django.contrib.auth.urls')),
]
# ===== OPTIONAL: Add commented-out URLs for future features =====
"""
# Uncomment these when you implement these features:

# Chat functionality
path('job/<int:job_id>/chat/', views.job_chat, name='job_chat'),

# Job actions
path('job/<int:job_id>/start/', views.start_job, name='start_job'),
path('job/<int:job_id>/complete/', views.complete_job, name='complete_job'),

# Application handling
path('application/<int:application_id>/accept/', views.accept_application, name='accept_application'),

# Payment and reviews
path('job/<int:job_id>/payment/', views.payment_page, name='payment_page'),
path('job/<int:job_id>/review/', views.leave_review, name='leave_review'),

# Legacy support (remove eventually)
path('my-jobs-old/', views.my_jobs, name='my_jobs'),
path('custom-login/', views.custom_login, name='custom_login'),
path('accounts/logout/', views.logout_view, name='auth_logout'),
"""