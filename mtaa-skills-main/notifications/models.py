#from django.db import models
# Create your models here.


from django.db import models
from django.conf import settings
from django.utils import timezone

class Notification(models.Model):
    NOTIFICATION_TYPES = [
        ('job_assigned', 'Job Assigned'),
        ('job_completed', 'Job Completed'),
        ('payment_received', 'Payment Received'),
        ('new_review', 'New Review'),
        ('new_message', 'New Message'),
        ('system', 'System Notification'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    related_object_id = models.PositiveIntegerField(null=True, blank=True)
    related_object_type = models.CharField(max_length=50, null=True, blank=True)  # e.g., 'booking', 'job', 'review'
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"
    
    @property
    def is_recent(self):
        return (timezone.now() - self.created_at).seconds < 300  # 5 minutes
    
    def mark_as_read(self):
        self.is_read = True
        self.save()

class NotificationPreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notification_preferences')
    email_job_alerts = models.BooleanField(default=True)
    email_messages = models.BooleanField(default=True)
    email_payments = models.BooleanField(default=True)
    email_reviews = models.BooleanField(default=True)
    push_notifications = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
