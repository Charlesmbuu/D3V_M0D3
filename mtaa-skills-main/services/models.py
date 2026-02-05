from django.db import models
from django.urls import reverse
from users.models import User

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100, unique=True, db_index=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    
    class Meta:
        verbose_name_plural = "Service Categories"
        ordering = ['name']
        indexes = [
            models.Index(fields=['name', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return f"/category/{self.id}/"

class ServiceProvider(models.Model):
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='service_provider',
        db_index=True
    )
    business_name = models.CharField(max_length=200, db_index=True)
    service_categories = models.ManyToManyField(
        ServiceCategory, 
        related_name='providers',
        blank=True
    )
    description = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Contact Information
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    location = models.CharField(max_length=100, blank=True, db_index=True)
    
    # Professional Information
    experience_years = models.IntegerField(default=0)
    profile_picture = models.ImageField(upload_to='provider_pics/', blank=True, null=True)
    
    # Status and Verification
    is_active = models.BooleanField(default=True, db_index=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    
    # Performance Metrics
    total_jobs_completed = models.IntegerField(default=0, db_index=True)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0, db_index=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['is_active', 'is_verified']),
            models.Index(fields=['location', 'is_active']),
            models.Index(fields=['average_rating', 'is_active']),
        ]
    
    def __str__(self):
        return self.business_name
    
    def get_absolute_url(self):
        # Fastest approach - direct URL construction
        return f"/providers/{self.id}/"
    
    @property
    def primary_category(self):
        """Fast property access to first category"""
        return self.service_categories.first()
    
    @property 
    def is_available_for_jobs(self):
        """Optimized availability check"""
        return self.is_active and self.service_categories.exists()
    
    def update_metrics(self):
        """Fast metrics update method"""
        from django.db.models import Count, Avg
        from bookings.models import Booking
        
        stats = Booking.objects.filter(
            provider=self, 
            status='completed'
        ).aggregate(
            total_completed=Count('id'),
            avg_rating=Avg('review__stars')
        )
        
        self.total_jobs_completed = stats['total_completed'] or 0
        self.average_rating = stats['avg_rating'] or 0.0
        self.save(update_fields=['total_jobs_completed', 'average_rating', 'updated_at'])