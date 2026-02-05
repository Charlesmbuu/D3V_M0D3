from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Prefetch
from django.utils import timezone
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.views.decorators.http import require_http_methods
from .models import Job, Booking
from .forms import JobForm, BookingForm
from services.models import ServiceProvider, ServiceCategory


@login_required
def post_job(request):
    """Customers post new job requests"""
    if request.user.user_type != 'customer':
        messages.error(request, 'Only customers can post jobs.')
        return redirect('home')
    


    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.customer = request.user
            job.save()
            messages.success(request, 'Job posted successfully! Providers can now apply.')
            return redirect('bookings:job_detail', job_id=job.id)
    else:
        form = JobForm()
    
    return render(request, 'bookings/post_job.html', {'form': form})

@login_required
@never_cache
def available_jobs(request):
    """
    Ultra-fast available jobs with optimized queries
    """
    try:
        # Single optimized query to get provider with categories
        provider = ServiceProvider.objects.only(
            'id'
        ).prefetch_related(
            'service_categories'
        ).get(user=request.user)
        
        provider_categories = provider.service_categories.all()
        
        if not provider_categories.exists():
            messages.warning(request, 
                "You haven't selected any service categories. Please update your profile to see available jobs."
            )
            return redirect('services:edit_provider_profile')
        
        # Optimized query with selective fields and indexing
        available_jobs = Job.objects.filter(
            service_category__in=provider_categories,
            status='posted',
            assigned_provider__isnull=True
        ).exclude(
            customer=request.user
        ).select_related(
            'customer', 'service_category'
        ).only(
            'id', 'title', 'description', 'budget', 'location', 
            'preferred_date', 'created_at', 'customer__username',
            'service_category__name'
        ).order_by('-created_at')
        
        context = {
            'available_jobs': available_jobs,
            'provider': provider,
        }
        return render(request, 'bookings/available_jobs.html', context)
        
    except ServiceProvider.DoesNotExist:
        messages.error(request, "You need to create a service provider profile first.")
        return redirect('become_provider')

@login_required
@never_cache
def job_detail(request, job_id):
    """
    Optimized job detail with minimal database hits
    """
    job = get_object_or_404(
        Job.objects.select_related(
            'customer', 'service_category', 'assigned_provider'
        ).prefetch_related(
            Prefetch(
                'booking_set',
                queryset=Booking.objects.select_related('provider').prefetch_related(
                    'payment_set', 'review'
                )
            )
        ),
        id=job_id
    )
    
    # Check permissions efficiently
    can_view = (
        request.user == job.customer or 
        (hasattr(request.user, 'service_provider') and 
         job.assigned_provider == request.user.service_provider)
    )
    
    if not can_view:
        messages.error(request, 'You cannot view this job.')
        return redirect('home')
    
    # Get booking efficiently
    booking = job.booking_set.first()
    
    # Handle provider application
    if request.method == 'POST' and hasattr(request.user, 'service_provider'):
        return _handle_job_application(request, job, booking)
    
    context = {
        'job': job,
        'booking': booking,
        'booking_form': BookingForm(),
    }
    return render(request, 'bookings/job_detail.html', context)

def _handle_job_application(request, job, existing_booking):
    """Optimized job application handler"""
    provider = request.user.service_provider
    
    if existing_booking:
        messages.info(request, 'This job already has a provider.')
        return redirect('bookings:job_detail', job_id=job.id)
    
    booking_form = BookingForm(request.POST)
    if booking_form.is_valid():
        with transaction.atomic():
            booking = booking_form.save(commit=False)
            booking.job = job
            booking.provider = provider
            booking.save()
            
            job.status = 'assigned'
            job.assigned_provider = provider
            job.save(update_fields=['status', 'assigned_provider', 'updated_at'])
            
            messages.success(request, 'Successfully applied for this job!')
            
        return redirect('bookings:job_detail', job_id=job.id)
    
    return render(request, 'bookings/job_detail.html', {
        'job': job,
        'booking': None,
        'booking_form': booking_form,
    })