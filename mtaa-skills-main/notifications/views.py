from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import Notification, NotificationPreference
from .manager import NotificationManager

@login_required
def notification_list(request):
    """Display user's notifications"""
    notifications = request.user.notifications.all()[:50]  # Last 50 notifications
    unread_count = request.user.notifications.filter(is_read=False).count()
    
    return render(request, 'notifications/notification_list.html', {
        'notifications': notifications,
        'unread_count': unread_count,
    })

@login_required
@login_required
def mark_as_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.mark_as_read()
    return redirect('notifications:list')

@login_required
def mark_all_as_read(request):
    """Mark all notifications as read"""
    request.user.notifications.filter(is_read=False).update(is_read=True)
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('notifications:list')

@login_required
def notification_preferences(request):
    """User notification preferences"""
    preferences, created = NotificationPreference.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        preferences.email_job_alerts = request.POST.get('email_job_alerts') == 'on'
        preferences.email_messages = request.POST.get('email_messages') == 'on'
        preferences.email_payments = request.POST.get('email_payments') == 'on'
        preferences.email_reviews = request.POST.get('email_reviews') == 'on'
        preferences.push_notifications = request.POST.get('push_notifications') == 'on'
        preferences.save()
        
        return redirect('notifications:preferences')
    
    return render(request, 'notifications/preferences.html', {
        'preferences': preferences,
    })

@login_required
def get_unread_count(request):
    """API endpoint for unread notification count"""
    count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': count})

@login_required
def get_recent_notifications(request):
    """API endpoint for recent notifications"""
    notifications = request.user.notifications.filter(is_read=False)[:5]
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.notification_type,
        'created_at': n.created_at.strftime('%H:%M'),
        'is_recent': n.is_recent,
    } for n in notifications]
    
    return JsonResponse({'notifications': data})
