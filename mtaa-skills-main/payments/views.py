from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.views.decorators.http import require_http_methods
import json
import random
import time
from datetime import datetime

from .models import Payment, MpesaTransaction
from bookings.models import Booking
from services.models import ServiceProvider
from payments.models import ProviderWallet
from notifications.manager import NotificationManager

def get_client_ip(request):
    """Get the client's IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class MpesaSimulator:
    """Enhanced M-Pesa simulator that mimics real-world behavior"""
    
    @staticmethod
    def generate_receipt_number():
        """Generate realistic M-Pesa receipt number"""
        return f"RB{random.randint(10000, 99999)}{random.randint(1000, 9999)}"
    
    @staticmethod
    def generate_transaction_id():
        """Generate realistic transaction ID"""
        return f"O4A{random.randint(100, 999)}ABCD{random.randint(10000, 99999)}"
    
    @staticmethod
    def simulate_processing_delay():
        """Simulate real M-Pesa processing delay"""
        time.sleep(2)  # 2-second delay for realism
    
    @staticmethod
    def validate_phone_number(phone_number):
        """Validate Kenyan phone number format"""
        if not phone_number:
            return False, "Phone number is required"
        
        # Clean the phone number
        cleaned_phone = phone_number.strip().replace('+', '').replace(' ', '')
        
        # Check if it's a valid Kenyan number
        if cleaned_phone.startswith('254') and len(cleaned_phone) == 12:
            return True, cleaned_phone
        elif cleaned_phone.startswith('0') and len(cleaned_phone) == 10:
            # Convert to international format
            cleaned_phone = '254' + cleaned_phone[1:]
            return True, cleaned_phone
        elif len(cleaned_phone) == 9 and cleaned_phone.startswith('7'):
            cleaned_phone = '254' + cleaned_phone
            return True, cleaned_phone
        else:
            return False, "Invalid phone number format. Use: 07XXXXXXXX or 2547XXXXXXXX"

@login_required
def initiate_payment(request, booking_id):
    """Initiate M-Pesa payment for a booking with enhanced simulation"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user is the customer for this booking
    if booking.job.customer != request.user:
        messages.error(request, 'You are not authorized to pay for this booking.')
        return redirect('job_detail', job_id=booking.job.id)
    
    # Check if booking is confirmed
    if not booking.customer_confirmed_at:
        messages.error(request, 'Please confirm job completion before making payment.')
        return redirect('job_detail', job_id=booking.job.id)
    
    # Check if payment already exists and is successful
    existing_payment = Payment.objects.filter(booking=booking, status='success').first()
    if existing_payment:
        messages.info(request, 'Payment already completed for this booking.')
        return redirect('job_detail', job_id=booking.job.id)
    
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        actual_amount = float(booking.agreed_price)
        
        if not phone_number:
            messages.error(request, 'Please provide your phone number.')
            return render(request, 'payments/initiate_payment.html', {'booking': booking})
        
        # Validate phone number
        is_valid, result = MpesaSimulator.validate_phone_number(phone_number)
        if not is_valid:
            messages.error(request, result)
            return render(request, 'payments/initiate_payment.html', {'booking': booking})
        
        validated_phone = result
        
        # Create payment record
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.agreed_price,
            phone_number=validated_phone,
            description=f'Payment for {booking.job.title}',
            status='initiated'
        )
        
        print(f"🔄 Initiating simulated M-Pesa payment: {validated_phone}, Amount: KSh {actual_amount}")
        
        # Process enhanced simulated payment
        return process_enhanced_simulated_payment(payment, validated_phone, actual_amount, request)
    
    return render(request, 'payments/initiate_payment.html', {
        'booking': booking,
        'is_sandbox': True,
    })

def process_enhanced_simulated_payment(payment, phone_number, amount, request):
    """Process an enhanced simulated payment that mimics real M-Pesa flow"""
    
    # Simulate processing delay
    MpesaSimulator.simulate_processing_delay()
    
    # Generate realistic transaction details
    receipt_number = MpesaSimulator.generate_receipt_number()
    transaction_id = MpesaSimulator.generate_transaction_id()
    
    # Update payment with success status
    payment.status = 'success'
    payment.mpesa_receipt = receipt_number
    payment.transaction_id = transaction_id
    payment.result_description = 'Success. The service request has been completed successfully.'
    payment.completed_at = timezone.now()
    payment.save()
    
    # Update booking status
    booking = payment.booking
    booking.is_paid = True
    booking.paid_at = timezone.now()
    booking.save()
    
    # Update provider wallet
    try:
        provider = booking.provider
        wallet, created = ProviderWallet.objects.get_or_create(provider=provider)
        wallet.balance += payment.amount
        wallet.total_earnings += payment.amount
        wallet.last_updated = timezone.now()
        wallet.save()
        
        # Log wallet transaction
        print(f"💰 Wallet updated: {provider.business_name} +KSh {payment.amount}")
    except Exception as e:
        print(f"❌ Wallet update error: {e}")
    
    # Log detailed simulation transaction
    MpesaTransaction.objects.create(
        payment=payment,
        transaction_type='simulation_success',
        request_data=json.dumps({
            'phone_number': phone_number, 
            'amount': amount,
            'timestamp': datetime.now().isoformat()
        }),
        response_data=json.dumps({
            'status': 'success',
            'receipt_number': receipt_number,
            'transaction_id': transaction_id,
            'amount': amount,
            'phone_number': phone_number,
            'timestamp': datetime.now().isoformat(),
            'message': 'The service request has been completed successfully.'
        }),
        ip_address=get_client_ip(request)
    )
    
    # Send notifications
    try:
        NotificationManager.notify_payment_received(booking.provider, payment)
        NotificationManager.notify_payment_completed(booking.job.customer, payment)
    except Exception as e:
        print(f"📢 Notification error: {e}")
    
    # Success message with realistic details
    success_message = f'''
    ✅ Payment Successful!
    
    Amount: KSh {amount:,.2f}
    To: {booking.provider.business_name}
    Phone: {phone_number}
    Receipt: {receipt_number}
    Transaction ID: {transaction_id}
    Time: {payment.completed_at.strftime("%Y-%m-%d %H:%M:%S")}
    
    Thank you for using M-Pesa!
    '''
    
    messages.success(request, success_message)
    print(f"✅ Simulated M-Pesa payment successful for {phone_number}")
    
    return redirect('payment_success', payment_id=payment.id)

@login_required
def payment_success(request, payment_id):
    """Display enhanced payment success page"""
    payment = get_object_or_404(Payment, id=payment_id)
    
    # Verify user has permission to view this payment
    if payment.booking.job.customer != request.user and payment.booking.provider.user != request.user:
        messages.error(request, 'You are not authorized to view this payment.')
        return redirect('home')
    
    return render(request, 'payments/payment_success.html', {
        'payment': payment,
        'booking': payment.booking,
        'transaction_time': payment.completed_at or timezone.now(),
    })

@login_required
def payment_status(request, booking_id):
    """Enhanced payment status page with realistic details"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check if user is authorized to view this payment status
    if booking.job.customer != request.user and booking.provider.user != request.user:
        messages.error(request, 'You are not authorized to view this payment status.')
        return redirect('home')
    
    # Try to get payment if it exists
    try:
        payment = Payment.objects.get(booking=booking)
        mpesa_transactions = MpesaTransaction.objects.filter(payment=payment).order_by('-created_at')
        
        # Generate realistic status timeline
        status_timeline = [
            {
                'status': 'Initiated',
                'time': payment.created_at,
                'description': 'Payment request sent to M-Pesa',
                'icon': '📱',
                'completed': True
            },
            {
                'status': 'Processing',
                'time': payment.created_at + timezone.timedelta(seconds=30),
                'description': 'Processing your payment',
                'icon': '🔄',
                'completed': payment.status in ['success', 'failed']
            },
            {
                'status': 'Completed' if payment.status == 'success' else 'Failed',
                'time': payment.completed_at if payment.completed_at else payment.created_at + timezone.timedelta(minutes=1),
                'description': payment.result_description or 'Payment processed',
                'icon': '✅' if payment.status == 'success' else '❌',
                'completed': True
            }
        ]
        
    except Payment.DoesNotExist:
        payment = None
        mpesa_transactions = None
        status_timeline = []
    
    return render(request, 'payments/payment_status.html', {
        'booking': booking,
        'payment': payment,
        'mpesa_transactions': mpesa_transactions,
        'status_timeline': status_timeline,
    })

@login_required
def simulate_mpesa_prompt(request, booking_id):
    """Interactive M-Pesa prompt simulation"""
    booking = get_object_or_404(Booking, id=booking_id)
    
    if booking.job.customer != request.user:
        messages.error(request, 'You are not authorized to access this page.')
        return redirect('home')
    
    if request.method == 'POST':
        # Handle PIN submission
        pin = request.POST.get('mpesa_pin')
        
        if not pin or len(pin) != 4 or not pin.isdigit():
            messages.error(request, 'Please enter a valid 4-digit M-Pesa PIN.')
            return render(request, 'payments/simulate_mpesa_prompt.html', {'booking': booking})
        
        # Process payment with PIN
        return process_payment_with_pin(booking, pin, request)
    
    return render(request, 'payments/simulate_mpesa_prompt.html', {
        'booking': booking,
        'amount': booking.agreed_price,
        'business_name': booking.provider.business_name,
    })

def process_payment_with_pin(booking, pin, request):
    """Process payment with PIN simulation"""
    
    # Create payment record
    payment = Payment.objects.create(
        booking=booking,
        amount=booking.agreed_price,
        phone_number=request.user.username,  # Using username as phone for simulation
        description=f'Payment for {booking.job.title}',
        status='processing'
    )
    
    # Simulate M-Pesa processing
    MpesaSimulator.simulate_processing_delay()
    
    # Generate realistic transaction details
    receipt_number = MpesaSimulator.generate_receipt_number()
    transaction_id = MpesaSimulator.generate_transaction_id()
    
    # Update payment status
    payment.status = 'success'
    payment.mpesa_receipt = receipt_number
    payment.transaction_id = transaction_id
    payment.result_description = 'Success. The service request has been completed successfully.'
    payment.completed_at = timezone.now()
    payment.save()
    
    # Update booking
    booking.is_paid = True
    booking.paid_at = timezone.now()
    booking.save()
    
    # Update provider wallet
    try:
        provider = booking.provider
        wallet, created = ProviderWallet.objects.get_or_create(provider=provider)
        wallet.balance += payment.amount
        wallet.total_earnings += payment.amount
        wallet.save()
    except Exception as e:
        print(f"Wallet update error: {e}")
    
    # Log transaction
    MpesaTransaction.objects.create(
        payment=payment,
        transaction_type='pin_simulation_success',
        request_data=json.dumps({'pin_entered': True}),
        response_data=json.dumps({
            'status': 'success',
            'receipt': receipt_number,
            'transaction_id': transaction_id
        }),
        ip_address=get_client_ip(request)
    )
    
    return redirect('payment_success', payment_id=payment.id)

@login_required
def payment_history(request):
    """View payment history for user"""
    if request.user.user_type == 'customer':
        # Customer sees payments they made
        payments = Payment.objects.filter(booking__job__customer=request.user).order_by('-created_at')
    else:
        # Provider sees payments they received
        try:
            provider = ServiceProvider.objects.get(user=request.user)
            payments = Payment.objects.filter(booking__provider=provider).order_by('-created_at')
        except ServiceProvider.DoesNotExist:
            payments = Payment.objects.none()
    
    return render(request, 'payments/payment_history.html', {
        'payments': payments,
        'user_type': request.user.user_type,
    })

# Keep your existing callback and other payment method views
@csrf_exempt
def mpesa_callback(request):
    """Handle M-Pesa payment callback (for real integration)"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print(f"M-Pesa Callback Received: {data}")
            
            # Your existing callback logic here
            return JsonResponse({'ResultCode': 0, 'ResultDesc': 'Success'})
            
        except Exception as e:
            print(f"Callback error: {e}")
            return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Error'})
    
    return JsonResponse({'ResultCode': 1, 'ResultDesc': 'Invalid method'})

# ... (keep your existing Stripe and PayPal views as they are)