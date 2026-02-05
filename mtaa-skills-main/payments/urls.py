from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Enhanced M-Pesa simulation routes
    path('initiate/<int:booking_id>/', views.initiate_payment, name='initiate_payment'),
    path('simulate-prompt/<int:booking_id>/', views.simulate_mpesa_prompt, name='simulate_mpesa_prompt'),
    path('success/<int:payment_id>/', views.payment_success, name='payment_success'),
    path('status/<int:booking_id>/', views.payment_status, name='payment_status'),
    path('history/', views.payment_history, name='payment_history'),
    
    # Real M-Pesa callback (for future integration)
    path('callback/mpesa/', views.mpesa_callback, name='mpesa_callback'),
    
    # Other payment methods
    path('stripe/<int:booking_id>/', views.initiate_stripe_payment, name='initiate_stripe_payment'),
    path('paypal/<int:booking_id>/', views.initiate_paypal_payment, name='initiate_paypal_payment'),
    
    # Legacy routes for compatibility
    path('booking/<int:booking_id>/pay/', views.initiate_payment, name='initiate_payment_legacy'),
    path('booking/<int:booking_id>/status/', views.payment_status, name='payment_status_legacy'),
]