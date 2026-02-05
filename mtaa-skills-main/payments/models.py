from django.db import models
from django.utils import timezone
from bookings.models import Booking
from services.models import ServiceProvider

class Payment(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('initiated', 'Initiated'),
        ('processing', 'Processing'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    )
    
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    mpesa_receipt = models.CharField(max_length=50, blank=True)
    transaction_id = models.CharField(max_length=100, blank=True)  # Added for simulation
    phone_number = models.CharField(max_length=15)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    description = models.TextField(blank=True)
    
    # M-Pesa API responses
    checkout_request_id = models.CharField(max_length=100, blank=True)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    result_code = models.IntegerField(null=True, blank=True)
    result_description = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payment KES {self.amount} - {self.status}"
    
    class Meta:
        ordering = ['-created_at']

class MpesaTransaction(models.Model):
    """Store all M-Pesa transaction logs"""
    TRANSACTION_TYPES = (
        ('stk_push', 'STK Push'),
        ('callback', 'Callback'),
        ('simulation_success', 'Simulation Success'),
        ('simulation_failed', 'Simulation Failed'),
        ('pin_simulation_success', 'PIN Simulation Success'),
    )
    
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True, related_name='transactions')
    transaction_type = models.CharField(max_length=50, choices=TRANSACTION_TYPES)
    request_data = models.TextField()
    response_data = models.TextField()
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.transaction_type} - {self.created_at}"
    
    class Meta:
        ordering = ['-created_at']

class ProviderWallet(models.Model):
    provider = models.OneToOneField(
        ServiceProvider, 
        on_delete=models.CASCADE,
        related_name='wallet'
    )
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # Added field
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_updated = models.DateTimeField(auto_now=True)  # Added for tracking
    
    def __str__(self):
        return f"{self.provider.business_name} - KES {self.balance}"
    
    class Meta:
        verbose_name = "Provider Wallet"
        verbose_name_plural = "Provider Wallets"

# Add this to your existing models.py