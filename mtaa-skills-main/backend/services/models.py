from django.db import models
from users.models import User

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    
    def __str__(self):
        return self.name

class ServiceProvider(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    service_categories = models.ManyToManyField(ServiceCategory)
    description = models.TextField()
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    def __str__(self):
        return self.business_name
