from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Review, ProviderStats
from .forms import ReviewForm
from bookings.models import Booking
from notifications.manager import NotificationManager

@login_required
def create_review(request, booking_id):
    """Create a review for a completed booking"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user can review this booking
    if booking.job.customer != request.user:
        messages.error(request, 'You can only review your own bookings.')
        return redirect('job_detail', job_id=booking.job.id)
    
    # Check if booking is completed and paid
    if not booking.is_paid:
        messages.error(request, 'You can only review completed and paid bookings.')
        return redirect('job_detail', job_id=booking.job.id)
    
    # Check if review already exists
    if hasattr(booking, 'review'):
        messages.info(request, 'You have already reviewed this booking.')
        return redirect('job_detail', job_id=booking.job.id)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.reviewer = request.user
            review.provider = booking.assigned_provider
            review.is_verified = True  # Since booking is paid
            review.save()

			# Create notification for provider
			NotificationManager.notify_new_review(review.provider, review)
            
            # Update provider stats
            stats, created = ProviderStats.objects.get_or_create(provider=booking.assigned_provider)
            stats.update_stats()
            
            messages.success(request, 'Thank you for your review!')
            return redirect('job_detail', job_id=booking.job.id)
    else:
        form = ReviewForm()
    
    return render(request, 'reviews/create_review.html', {
        'form': form,
        'booking': booking,
        'provider': booking.assigned_provider,
    })

@login_required
def provider_reviews(request, provider_id):
    """Display all reviews for a provider"""
    from services.models import ServiceProvider
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    reviews = provider.reviews.filter(is_verified=True).select_related('reviewer', 'booking')
    
    return render(request, 'reviews/provider_reviews.html', {
        'provider': provider,
        'reviews': reviews,
    })

def provider_stats_api(request, provider_id):
    """API endpoint for provider statistics"""
    from services.models import ServiceProvider
    provider = get_object_or_404(ServiceProvider, id=provider_id)
    stats, created = ProviderStats.objects.get_or_create(provider=provider)
    
    return JsonResponse({
        'average_rating': float(stats.average_rating),
        'total_reviews': stats.total_reviews,
        'rating_breakdown': stats.rating_breakdown,
    })
