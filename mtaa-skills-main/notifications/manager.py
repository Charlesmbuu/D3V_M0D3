from django.db import models
from django.conf import settings

class NotificationManager:
    @staticmethod
    def create_notification(user, notification_type, title, message, related_object=None):
        from .models import Notification
        
        related_object_id = None
        related_object_type = None
        
        if related_object:
            related_object_id = related_object.id
            related_object_type = related_object._meta.model_name
        
        notification = Notification.objects.create(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            related_object_id=related_object_id,
            related_object_type=related_object_type
        )
        
        # In a real-time system, we'd send this via WebSockets
        # For now, we'll store it and display on next page load
        return notification
    
    @staticmethod
    def notify_job_assigned(provider, job):
        title = "New Job Assignment"
        message = f"You've been assigned to: {job.title}"
        return NotificationManager.create_notification(
            provider.user, 'job_assigned', title, message, job
        )
    
    @staticmethod
    def notify_job_completed(customer, job):
        title = "Job Completed"
        message = f"Your job '{job.title}' has been completed. Please confirm and make payment."
        return NotificationManager.create_notification(
            customer, 'job_completed', title, message, job
        )
    
    @staticmethod
    def notify_payment_received(provider, payment):
        title = "Payment Received"
        message = f"Payment of KSh {payment.amount} received for {payment.booking.job.title}"
        return NotificationManager.create_notification(
            provider.user, 'payment_received', title, message, payment
        )
    
    @staticmethod
    def notify_new_review(provider, review):
        title = "New Review Received"
        message = f"You received a {review.rating}-star review for {review.booking.job.title}"
        return NotificationManager.create_notification(
            provider.user, 'new_review', title, message, review
        )
