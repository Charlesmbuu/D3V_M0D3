from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError, transaction
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from .models import ServiceProvider, ServiceCategory
from .forms import ServiceProviderForm

@never_cache
def provider_list(request):
    """Simple provider listing"""
    providers = ServiceProvider.objects.filter(is_active=True).select_related('user')
    return render(request, 'services/provider_list.html', {'providers': providers})

@never_cache
def category_detail(request, pk):
    """Category detail view"""
    category = get_object_or_404(ServiceCategory, pk=pk, is_active=True)
    providers = ServiceProvider.objects.filter(
        service_categories=category, 
        is_active=True
    ).select_related('user')
    return render(request, 'services/category_detail.html', {
        'category': category,
        'providers': providers
    })

def home(request):
    """Services home page"""
    categories = ServiceCategory.objects.filter(is_active=True)
    return render(request, 'services/home.html', {'categories': categories})



@login_required
@never_cache
@require_http_methods(["GET", "POST"])
def become_provider(request):
    """
    Optimized provider creation with atomic transactions and caching
    """
    # Fast existence check using select_related
    if hasattr(request.user, 'service_provider'):
        messages.info(request, 'You already have a provider profile.')
        return redirect('services:provider_dashboard')
        
    
    if request.method == 'POST':
        form = ServiceProviderForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    provider = form.save(commit=False)
                    provider.user = request.user
                    provider.save()
                    form.save_m2m()  # Save many-to-many data
                    
                    messages.success(request, 'Provider profile created successfully!')
                    return redirect('services:provider_dashboard')
                    
            except IntegrityError:
                messages.error(request, 'You already have a provider profile.')
                return redirect('services:provider_dashboard')
    else:
        form = ServiceProviderForm()
    
    # Prefetch categories for faster template rendering
    categories = ServiceCategory.objects.filter(is_active=True).only('id', 'name')
    
    return render(request, 'services/become_provider.html', {
        'form': form,
        'categories': categories,
    })

@never_cache
def provider_detail(request, provider_id):
    """
    Optimized provider detail view with selective prefetching
    """
    provider = get_object_or_404(
        ServiceProvider.objects.select_related('user').prefetch_related(
            'service_categories'
        ).only(
            'business_name', 'description', 'hourly_rate', 'location',
            'experience_years', 'profile_picture', 'is_verified',
            'total_jobs_completed', 'average_rating'
        ),
        id=provider_id, 
        is_active=True
    )
    
    return render(request, 'services/provider_detail.html', {
        'provider': provider,
    })

@login_required
def service_list(request):
    return render(request, 'services/service_list.html', {
        'title': 'Services'
    })

@login_required
@never_cache
def provider_dashboard(request):
    """
    Fast dashboard with optimized queries
    """
    try:
        provider = ServiceProvider.objects.select_related('user').get(
            user=request.user, 
            is_active=True
        )
        
        # Optimized related data fetching
        from bookings.models import Job, Booking
        from django.db.models import Count, Q
        
        stats = {
            'active_jobs': Job.objects.filter(
                assigned_provider=provider, 
                status__in=['assigned', 'in_progress']
            ).count(),
            'completed_jobs': Job.objects.filter(
                assigned_provider=provider, 
                status='completed'
            ).count(),
            'available_jobs': Job.objects.filter(
                service_category__in=provider.service_categories.all(),
                status='posted',
                assigned_provider__isnull=True
            ).count(),
        }
        
        return render(request, 'home_provider.html', {
            'provider': provider,
            'stats': stats,
        })
        
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Please create a provider profile first.')
        return redirect('services:become_provider')

