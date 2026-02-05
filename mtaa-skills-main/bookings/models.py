from django.db import models
from django.utils import timezone
from django.urls import reverse
from users.models import User

class Job(models.Model):
    STATUS_CHOICES = (
        ('posted', 'Posted - Looking for providers'),
        ('assigned', 'Assigned to provider'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_jobs')
    service_category = models.ForeignKey('services.ServiceCategory', on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    location = models.CharField(max_length=200)
    preferred_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='posted')
    
    # Provider who accepted the job (nullable until assigned)
    assigned_provider = models.ForeignKey('services.ServiceProvider', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Completion fields
    work_completed_at = models.DateTimeField(null=True, blank=True)
    customer_confirmed_at = models.DateTimeField(null=True, blank=True)
    customer_notes = models.TextField(blank=True)
    provider_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'service_category']),
            models.Index(fields=['status', 'assigned_provider']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.customer.username}"
    
    def get_absolute_url(self):
        return reverse('bookings:job_detail', kwargs={'job_id': self.id})
    
    def is_available(self):
        return self.status == 'posted' and self.assigned_provider is None

class Booking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    
    job = models.OneToOneField(Job, on_delete=models.CASCADE)
    provider = models.ForeignKey('services.ServiceProvider', on_delete=models.CASCADE)
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
    scheduled_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Communication fields
    customer_message = models.TextField(blank=True)
    provider_message = models.TextField(blank=True)
    
    # Completion fields
    work_completed_at = models.DateTimeField(null=True, blank=True)
    customer_confirmed_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status', 'customer_confirmed_at']),
            models.Index(fields=['provider', 'status']),
            models.Index(fields=['job', 'status']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Booking: {self.job.title} - {self.provider.business_name}"
    
    def save(self, *args, **kwargs):
        # Auto-update job status when booking status changes
        if self.status == 'confirmed' and self.job.status != 'assigned':
            self.job.status = 'assigned'
            self.job.assigned_provider = self.provider
            self.job.save()
        super().save(*args, **kwargs)