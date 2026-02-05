from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Poor'),
        (2, '2 - Fair'),
        (3, '3 - Good'),
        (4, '4 - Very Good'),
        (5, '5 - Excellent'),
    ]
    
    booking = models.OneToOneField('bookings.Booking', on_delete=models.CASCADE, related_name='review')
    reviewer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews_given')  # 👈 FIXED
    provider = models.ForeignKey('services.ServiceProvider', on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=RATING_CHOICES, validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ['booking', 'reviewer']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review for {self.provider.business_name} by {self.reviewer.username}"
    
    @property
    def stars(self):
        return '⭐' * self.rating

class ProviderStats(models.Model):
    provider = models.OneToOneField('services.ServiceProvider', on_delete=models.CASCADE, related_name='stats')
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.PositiveIntegerField(default=0)
    rating_breakdown = models.JSONField(default=dict)
    last_updated = models.DateTimeField(auto_now=True)
    
    def update_stats(self):
        from django.db.models import Avg
        reviews = self.provider.reviews.filter(is_verified=True)
        self.total_reviews = reviews.count()
        
        if self.total_reviews > 0:
            avg_result = reviews.aggregate(avg_rating=Avg('rating'))
            self.average_rating = avg_result['avg_rating'] or 0.00
            
            breakdown = {i: 0 for i in range(1, 6)}
            for review in reviews:
                breakdown[review.rating] += 1
            self.rating_breakdown = breakdown
        else:
            self.average_rating = 0.00
            self.rating_breakdown = {i: 0 for i in range(1, 6)}
        
        self.save()
    
    def __str__(self):
        return f"Stats for {self.provider.business_name}"
