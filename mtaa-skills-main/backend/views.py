from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model
from decimal import Decimal, InvalidOperation
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

# Your models
from bookings.models import Job, Booking
from services.models import ServiceCategory, ServiceProvider
from payments.models import ProviderWallet, Payment
from backend.models import UserProfile
from django.db.models import Q, Avg, Count
from django.utils import timezone

User = get_user_model()



# ======== GENERAL FUNCTIONS FOR BOTH USER_TYPES ===========
def login_view(request):
    role = request.GET.get('role', 'customer')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html', {'role': role})

def custom_login(request):
    role = request.GET.get('role', 'customer')  # Get selected role
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {
        'form': form,
        'role': role
    })

def register(request):
    role = request.GET.get('role', 'customer')
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save(commit=False)
                user.user_type = role
                user.save()

                # Create UserProfile with selected role
                UserProfile.objects.create(user=user, role=role)
                
                # Auto-login after registration
                login(request, user)
                
                messages.success(request, f'Account created successfully! Welcome to Mtaa Skills as a {role}.')
                return redirect('home')
            except Exception as e:
                messages.error(request, f'Error creating account: {str(e)}')
                print(f"Registration error: {e}")  # Debug logging
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'registration/register.html', {
        'form': form,
        'role': role
    })

def home(request):
    if request.user.is_authenticated:
        try:
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(
                user=request.user,
                defaults={'role': request.user.user_type if hasattr(request.user, 'user_type') else 'customer'}
            )
            
            if request.user.user_type == 'customer':
                # Count customer jobs for dashboard
                jobs_posted = Job.objects.filter(customer=request.user).count()
                active_jobs = Job.objects.filter(customer=request.user, status__in=['open', 'assigned', 'in_progress']).count()
                completed_jobs = Job.objects.filter(customer=request.user, status='completed').count()
                
                return render(request, 'home_customer.html', {
                    'user': request.user,
                    'profile': profile,
                    'jobs_posted': jobs_posted,
                    'active_jobs': active_jobs,
                    'completed_jobs': completed_jobs,
                })
            else:
                # Provider dashboard stats
                try:
                    provider = ServiceProvider.objects.get(user=request.user)
                    # Use assigned_provider instead of provider
                    my_jobs_count = Job.objects.filter(assigned_provider=provider).count()
                    active_jobs_count = Job.objects.filter(assigned_provider=provider, status__in=['assigned', 'in_progress']).count()
                    completed_jobs_count = Job.objects.filter(assigned_provider=provider, status='completed').count()
                    
                    # Get available jobs in their field
                    available_jobs_count = Job.objects.filter(
                        status='open',
                        service_category__in=provider.service_categories.all()
                    ).exclude(assigned_provider=provider).count()
                    
                except ServiceProvider.DoesNotExist:
                    my_jobs_count = 0
                    active_jobs_count = 0
                    completed_jobs_count = 0
                    available_jobs_count = 0
                    provider = None
                
                return render(request, 'home_provider.html', {
                    'user': request.user,
                    'profile': profile,
                    'provider': provider,
                    'my_jobs_count': my_jobs_count,
                    'active_jobs_count': active_jobs_count,
                    'completed_jobs_count': completed_jobs_count,
                    'available_jobs_count': available_jobs_count,
                })
                
        except Exception as e:
            # Fallback if anything goes wrong
            print(f"Home view error: {e}")  # For debugging
            return render(request, 'home_customer.html', {
                'user': request.user,
                'jobs_posted': 0,
                'active_jobs': 0,
                'completed_jobs': 0,
            })
    else:
        return render(request, 'home_public.html')

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile(request):
    profile = UserProfile.objects.get(user=request.user)
    
    if request.method == 'POST':
        # Handle role change
        new_role = request.POST.get('role')
        if new_role in ['customer', 'provider']:
            profile.role = new_role
            profile.save()
            messages.success(request, f'Profile updated! You are now a {new_role}.')
            return redirect('home')
    
    return render(request, 'profile.html', {
        'user': request.user,
        'profile': profile
    })

@login_required
def redirect_my_jobs(request):
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Check if user is a service provider
    try:
        if hasattr(request.user, 'serviceprovider'):
            return redirect('provider_jobs')
    except:
        pass
    
    # Default to customer jobs
    return redirect('customer_jobs')

# ===== CUSTOMER FUNCTIONALITY =====

@login_required
def browse_providers(request):
    category_id = request.GET.get('category')
    location = request.GET.get('location')
    
    providers = ServiceProvider.objects.filter(is_verified=True)
    
    if category_id:
        providers = providers.filter(categories__id=category_id)
    if location:
        providers = providers.filter(location__icontains=location)
    
    # Add average ratings
    providers = providers.annotate(avg_rating=Avg('reviews__rating'))
    
    categories = ServiceCategory.objects.all()
    
    return render(request, 'browse_providers.html', {
        'providers': providers,
        'categories': categories,
    })

@login_required
def customer_jobs(request):
    # Get jobs posted by the current customer
    customer_jobs = Job.objects.filter(customer=request.user).order_by('-created_at')
    
    # Count different statuses for dashboard stats
    total_jobs = customer_jobs.count()
    pending_jobs = customer_jobs.filter(status='pending').count()
    in_progress_jobs = customer_jobs.filter(status='in_progress').count()
    completed_jobs = customer_jobs.filter(status='completed').count()
    
    return render(request, 'jobs/customer_jobs.html', {
        'customer_jobs': customer_jobs,
        'total_jobs': total_jobs,
        'pending_jobs': pending_jobs,
        'in_progress_jobs': in_progress_jobs,
        'completed_jobs': completed_jobs,
    })


@login_required
def provider_detail(request, provider_id):
    provider = get_object_or_404(ServiceProvider, id=provider_id, is_verified=True)
    reviews = provider.reviews.all().order_by('-created_at')
    similar_providers = ServiceProvider.objects.filter(
        categories__in=provider.categories.all(),
        is_verified=True
    ).exclude(id=provider.id).distinct()[:4]
    
    return render(request, 'provider_detail.html', {
        'provider': provider,
        'reviews': reviews,
        'similar_providers': similar_providers,
    })

@login_required
def job_chat(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user has permission to chat about this job
    can_chat = False
    if request.user == job.customer:
        can_chat = True
    elif hasattr(request.user, 'serviceprovider') and job.assigned_provider:
        if request.user.serviceprovider == job.assigned_provider:
            can_chat = True
    
    if not can_chat:
        messages.error(request, 'You do not have permission to chat about this job.')
        return redirect('home')
    
    # For now, just show a placeholder page
    return render(request, 'chat/job_chat.html', {
        'job': job,
    })

@login_required
def post_job(request):
    print(f"DEBUG: post_job called - Method: {request.method}, User: {request.user}")
    
    if request.method == 'POST':
        try:
            print("DEBUG: Processing POST request")
            print(f"DEBUG: Form data: {request.POST}")
            
            # Get and validate the budget value
            budget_str = request.POST.get('budget', '0')
            print(f"DEBUG: Budget string: {budget_str}")
            
            try:
                budget = Decimal(budget_str)
                print(f"DEBUG: Budget decimal: {budget}")
            except (InvalidOperation, ValueError) as e:
                print(f"DEBUG: Budget error: {e}")
                messages.error(request, 'Please enter a valid budget amount.')
                return render(request, 'jobs/post_job.html', {
                    'categories': ServiceCategory.objects.all()
                })
            
            # Validate that budget is positive
            if budget <= Decimal('0'):
                print("DEBUG: Budget not positive")
                messages.error(request, 'Budget must be greater than 0.')
                return render(request, 'jobs/post_job.html', {
                    'categories': ServiceCategory.objects.all()
                })
            
            # Get other form data
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            location = request.POST.get('location', '').strip()
            service_category_id = request.POST.get('service_category') or request.POST.get('category')
            
            print(f"DEBUG: Title: {title}")
            print(f"DEBUG: Description length: {len(description)}")
            print(f"DEBUG: Location: {location}")
            print(f"DEBUG: Category ID: {service_category_id}")
            
            # Validate required fields
            if not title or not description or not service_category_id:
                print("DEBUG: Missing required fields")
                messages.error(request, 'Title, description, and service category are required.')
                return render(request, 'jobs/post_job.html', {
                    'categories': ServiceCategory.objects.all()
                })
            
            try:
                service_category = ServiceCategory.objects.get(id=service_category_id)
                print(f"DEBUG: Found category: {service_category.name}")
            except ServiceCategory.DoesNotExist:
                print("DEBUG: Category not found")
                messages.error(request, 'Invalid service category selected.')
                return render(request, 'jobs/post_job.html', {
                    'categories': ServiceCategory.objects.all()
                })

            # Create the job
            print("DEBUG: Creating job...")
            job = Job.objects.create(
                customer=request.user,
                title=title,
                description=description,
                budget=budget,
                location=location,
                service_category=service_category,
                status='open'
            )
            
            print(f"DEBUG: Job created successfully - ID: {job.id}")
            messages.success(request, f'Job "{title}" posted successfully! Professionals can now apply.')
            
            # Redirect to the job detail page
            return redirect('job_detail', job_id=job.id)
            
        except Exception as e:
            print(f"DEBUG: Job creation error: {str(e)}")
            messages.error(request, f'Error creating job: {str(e)}')
            return render(request, 'jobs/post_job.html', {
                'categories': ServiceCategory.objects.all()
            })
    
    else:
        # GET request - show the form
        print("DEBUG: GET request - showing form")
        categories = ServiceCategory.objects.all()
        return render(request, 'jobs/post_job.html', {
            'categories': categories
        })

@login_required
def job_detail(request, job_id):
    print(f"DEBUG: job_detail called for job {job_id} by user {request.user}")
    
    # Get the job - remove the customer restriction
    try:
        job = Job.objects.get(id=job_id)
        print(f"DEBUG: Found job {job.id} - Customer: {job.customer}, Assigned Provider: {job.assigned_provider}")
    except Job.DoesNotExist:
        messages.error(request, 'Job not found.')
        return redirect('home')
    
    # Check if user has permission to view this job
    can_view = False
    user_is_customer = request.user == job.customer
    user_is_assigned_provider = False
    
    if hasattr(request.user, 'serviceprovider'):
        try:
            provider = ServiceProvider.objects.get(user=request.user)
            user_is_assigned_provider = (job.assigned_provider == provider)
            print(f"DEBUG: User is provider: {provider}, Assigned provider match: {user_is_assigned_provider}")
        except ServiceProvider.DoesNotExist:
            print("DEBUG: User has no serviceprovider profile")
    
    can_view = user_is_customer or user_is_assigned_provider
    print(f"DEBUG: Permission check - Customer: {user_is_customer}, Provider: {user_is_assigned_provider}, Can View: {can_view}")
    
    if not can_view:
        messages.error(request, 'You do not have permission to view this job.')
        print("DEBUG: Redirecting to home - no permission")
        return redirect('home')
    
    # Get booking information
    try:
        booking = job.booking
        bookings = [booking] if booking else []
        print(f"DEBUG: Found {len(bookings)} bookings")
    except Exception as e:
        print(f"DEBUG: Booking error: {e}")
        bookings = []
    
    # FIX: Remove messages since Job model doesn't have messages field
    # messages_list = job.messages.all().order_by('timestamp')
    messages_list = []  # Empty list for now
    
    print(f"DEBUG: Rendering job detail template - user can edit: {request.user == job.customer}")
    return render(request, 'jobs/job_detail.html', {
        'job': job,
        'bookings': bookings,
     #   'messages': messages_list,
        'user_can_edit': request.user == job.customer,
    })

@login_required
def accept_application(request, application_id):
    application = get_object_or_404(JobApplication, id=application_id, job__customer=request.user)
    
    if application.job.status != 'open':
        messages.error(request, 'This job is no longer available.')
        return redirect('job_detail', job_id=application.job.id)
    
    # Accept this application and reject others
    JobApplication.objects.filter(job=application.job).update(is_accepted=False)
    application.is_accepted = True
    application.save()
    
    # Assign job to provider
    application.job.provider = application.provider
    application.job.status = 'assigned'
    application.job.save()
    
    messages.success(request, f'Job assigned to {application.provider.business_name}!')
    return redirect('job_detail', job_id=application.job.id)

@login_required
def complete_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, customer=request.user, status='in_progress')
    
    job.status = 'completed'
    job.completed_at = timezone.now()
    job.save()
    
    # Create payment record
    Payment.objects.create(
        job=job,
        amount=job.budget,
        mpesa_number=request.POST.get('mpesa_number', ''),
        status='pending'  # Simulated - would integrate with M-Pesa API
    )
    
    messages.success(request, 'Job marked as complete! Please proceed with payment.')
    return redirect('payment_page', job_id=job.id)

@login_required
def payment_page(request, job_id):
    job = get_object_or_404(Job, id=job_id, customer=request.user, status='completed')
    payment, created = Payment.objects.get_or_create(job=job)
    
    if request.method == 'POST':
        # Simulate M-Pesa payment
        payment.mpesa_number = request.POST.get('mpesa_number')
        payment.status = 'completed'  # Simulated success
        payment.completed_at = timezone.now()
        payment.save()
        
        # Update provider wallet
        wallet, created = ProviderWallet.objects.get_or_create(provider=job.provider)
        wallet.balance += job.budget
        wallet.total_earnings += job.budget
        wallet.save()
        
        messages.success(request, 'Payment completed successfully!')
        return redirect('leave_review', job_id=job.id)
    
    return render(request, 'payments/payment.html', {
        'job': job,
        'payment': payment,
    })

@login_required
def leave_review(request, job_id):
    job = get_object_or_404(Job, id=job_id, customer=request.user, status='completed')
    
    # Check if review already exists
    if hasattr(job, 'review'):
        messages.info(request, 'You have already reviewed this job.')
        return redirect('customer_dashboard')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        Review.objects.create(
            job=job,
            customer=request.user,
            provider=job.provider,
            rating=rating,
            comment=comment
        )
        
        messages.success(request, 'Thank you for your review!')
        return redirect('home')
    
    return render(request, 'reviews/leave_review.html', {
        'job': job,
    })

# ===== PROVIDER FUNCTIONALITY =====

@login_required
def available_jobs(request):
    # Only providers should see available jobs
    if request.user.user_type != 'provider':
        messages.error(request, 'Only service providers can browse available jobs.')
        return redirect('home')
    
    try:
        provider = ServiceProvider.objects.get(user=request.user)
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Please complete your service provider profile first.')
        return redirect('provider_profile')
    
    # Get provider's categories - FIX: Use service_categories
    provider_categories = provider.service_categories.all()
    
    # Show jobs in provider's categories by default
    jobs_in_my_field = Job.objects.filter(
        status='open',
        service_category__in=provider_categories
    ).exclude(booking__provider=provider)  # FIX: Use booking instead of bookings
    
    # Show jobs outside provider's categories when requested
    show_all = request.GET.get('show_all', False)
    if show_all:
        jobs = Job.objects.filter(status='open').exclude(
            booking__provider=provider  # FIX: Use booking instead of bookings
        )
    else:
        jobs = jobs_in_my_field
    
    category_id = request.GET.get('category')
    location = request.GET.get('location')
    
    if category_id:
        jobs = jobs.filter(service_category__id=category_id)
    if location:
        jobs = jobs.filter(location__icontains=location)
    
    categories = ServiceCategory.objects.all()
    
    return render(request, 'jobs/available_jobs.html', {
        'jobs': jobs,
        'categories': categories,
        'provider': provider,
        'jobs_in_my_field': jobs_in_my_field,
        'show_all': show_all,
    })

@login_required
def apply_job(request, job_id):
    print(f"🔧 DEBUG: apply_job called - Job: {job_id}, User: {request.user}")
    
    try:
        provider = ServiceProvider.objects.get(user=request.user)
        print(f"🔧 DEBUG: Found provider: {provider.business_name}")
    except ServiceProvider.DoesNotExist:
        print("❌ DEBUG: Provider profile not found")
        messages.error(request, 'Please complete your service provider profile first.')
        return redirect('provider_profile')
    
    try:
        job = get_object_or_404(Job, id=job_id, status='open')
        print(f"🔧 DEBUG: Found job: {job.title} (Status: {job.status})")
    except Job.DoesNotExist:
        print("❌ DEBUG: Job not found or not open")
        messages.error(request, 'Job not found or no longer available.')
        return redirect('available_jobs')
    
    if request.method == 'POST':
        print("🔧 DEBUG: Processing application POST")
        
        try:
            proposal = request.POST.get('proposal', '').strip()
            proposed_amount_str = request.POST.get('proposed_amount', '0')
            
            print(f"🔧 DEBUG: Proposal: {proposal[:50]}...")
            print(f"🔧 DEBUG: Proposed amount: {proposed_amount_str}")
            
            # Validate proposal
            if not proposal:
                messages.error(request, 'Please provide a proposal.')
                return render(request, 'jobs/apply_job.html', {
                    'job': job,
                    'provider': provider,
                })
            
            # Validate proposed amount
            try:
                proposed_amount = Decimal(proposed_amount_str)
                if proposed_amount <= 0:
                    messages.error(request, 'Proposed amount must be greater than 0.')
                    return render(request, 'jobs/apply_job.html', {
                        'job': job,
                        'provider': provider,
                    })
            except (InvalidOperation, ValueError):
                messages.error(request, 'Please enter a valid amount.')
                return render(request, 'jobs/apply_job.html', {
                    'job': job,
                    'provider': provider,
                })
            
            # Check if provider has already applied
            existing_booking = Booking.objects.filter(job=job, provider=provider).first()
            if existing_booking:
                messages.info(request, 'You have already applied for this job.')
                return redirect('available_jobs')
            
            # Create booking
            print("🔧 DEBUG: Creating booking...")
            booking = Booking.objects.create(
                job=job,
                provider=provider,
                proposal=proposal,
                proposed_amount=proposed_amount,
                agreed_price=proposed_amount,  # Initially same as proposed
                status='pending'
            )
            
            print(f"✅ DEBUG: Booking created successfully - ID: {booking.id}")
            messages.success(request, 'Application submitted successfully! The customer will review your proposal.')
            
            return redirect('available_jobs')
            
        except Exception as e:
            print(f"❌ DEBUG: Application error: {e}")
            messages.error(request, f'Error submitting application: {str(e)}')
            return render(request, 'jobs/apply_job.html', {
                'job': job,
                'provider': provider,
            })
    
    else:
        # GET request - show application form
        print("🔧 DEBUG: Showing application form")
        return render(request, 'jobs/apply_job.html', {
            'job': job,
            'provider': provider,
        })

def provider_jobs(request):
    # Check if user is a provider
    if not hasattr(request.user, 'serviceprovider'):
        messages.error(request, 'Only service providers can access this page.')
        return redirect('home')
    
    # Get provider instance
    try:
        provider = ServiceProvider.objects.get(user=request.user)
    except ServiceProvider.DoesNotExist:
        messages.error(request, 'Please complete your service provider profile first.')
        return redirect('provider_profile')
    
    # FIX: Use assigned_provider instead of provider
    assigned_jobs = Job.objects.filter(assigned_provider=provider).order_by('-created_at')
    
    # Get bookings for this provider
    try:
        bookings = Booking.objects.filter(provider=provider).select_related('job')
        applied_jobs = [booking.job for booking in bookings]
    except:
        applied_jobs = []
    
    # Count stats
    total_assigned = assigned_jobs.count()
    in_progress_jobs = assigned_jobs.filter(status='in_progress').count()
    completed_jobs = assigned_jobs.filter(status='completed').count()
    
    return render(request, 'jobs/provider_jobs.html', {
        'assigned_jobs': assigned_jobs,
        'applied_jobs': applied_jobs,
        'total_assigned': total_assigned,
        'in_progress_jobs': in_progress_jobs,
        'completed_jobs': completed_jobs,
        'provider': provider,
    })

@login_required
def my_jobs(request):
    """Legacy view for template compatibility - redirects to appropriate jobs page"""
    return redirect('redirect_my_jobs')

@login_required
def start_job(request, job_id):
    job = get_object_or_404(Job, id=job_id, provider__user=request.user, status='assigned')
    
    job.status = 'in_progress'
    job.save()
    
    messages.success(request, 'Job started! You can now communicate with the customer.')
    return redirect('job_chat', job_id=job.id)

@login_required
def job_chat(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    
    # Check if user is either customer or assigned provider
    if not (request.user == job.customer or 
            (job.provider and request.user == job.provider.user)):
        messages.error(request, 'You do not have permission to view this chat.')
        return redirect('home')
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content:
            Message.objects.create(
                job=job,
                sender=request.user,
                content=content
            )
        return redirect('job_chat', job_id=job.id)
    
    messages_list = job.messages.all().order_by('timestamp')
    
    return render(request, 'chat/job_chat.html', {
        'job': job,
        'messages': messages_list,
    })

@login_required
def provider_wallet(request):
    try:
        # Check if user is a service provider
        provider = ServiceProvider.objects.get(user=request.user)
        
        # Get or create wallet with proper defaults
        wallet, created = ProviderWallet.objects.get_or_create(
            provider=provider,
            defaults={
                'balance': 0.00,
                'total_earnings': 0.00
            }
        )
        
        if created:
            messages.info(request, "Your wallet has been created with a zero balance.")
        
        # Calculate actual stats
        completed_jobs_count = Job.objects.filter(
            assigned_provider=provider, 
            status='completed'
        ).count()
        
        # Get transactions from payments
        transactions = Payment.objects.filter(
            booking__provider=provider, 
            status='success'
        ).order_by('-created_at')[:10]
        
        # FIX: Calculate pending balance without is_paid lookup
        # Get completed jobs that don't have a successful payment
        completed_jobs_without_payment = Job.objects.filter(
            assigned_provider=provider,
            status='completed'
        ).exclude(
            id__in=Payment.objects.filter(status='success').values('booking__job__id')
        )
        
        pending_balance = sum(job.budget for job in completed_jobs_without_payment)
        
        # Calculate template values
        avg_job_value = 0
        if completed_jobs_count > 0 and wallet.total_earnings:
            avg_job_value = wallet.total_earnings / completed_jobs_count
        
        this_month_earnings = wallet.total_earnings * 0.3 if wallet.total_earnings else 0
        last_month_earnings = wallet.total_earnings * 0.2 if wallet.total_earnings else 0
        
        context = {
            'wallet': wallet,
            'provider': provider,
            'total_earnings': wallet.total_earnings,
            'completed_jobs': completed_jobs_count,
            'transactions': transactions,
            'pending_balance': pending_balance,
            'avg_job_value': avg_job_value,
            'this_month_earnings': this_month_earnings,
            'last_month_earnings': last_month_earnings,
        }
        return render(request, 'wallet/provider_wallet.html', context)
        
    except ServiceProvider.DoesNotExist:
        messages.error(request, "You need to be a service provider to access the wallet.")
        return redirect('provider_profile')
    except Exception as e:
        print(f"Wallet view error: {e}")
        messages.error(request, "An error occurred while loading your wallet.")
        return redirect('home')
        
@login_required
def provider_profile(request):
    try:
        provider = ServiceProvider.objects.get(user=request.user)
    except ServiceProvider.DoesNotExist:
        provider = None
    
    if request.method == 'POST':
        business_name = request.POST.get('business_name')
        description = request.POST.get('description')
        hourly_rate = request.POST.get('hourly_rate')
        location = request.POST.get('location')
        category_ids = request.POST.getlist('categories')
        
        if provider:
            provider.business_name = business_name
            provider.description = description
            provider.hourly_rate = hourly_rate
            provider.location = location
            provider.save()
            # FIX: Use service_categories instead of categories
            provider.service_categories.set(category_ids)
        else:
            provider = ServiceProvider.objects.create(
                user=request.user,
                business_name=business_name,
                description=description,
                hourly_rate=hourly_rate,
                location=location
            )
            provider.service_categories.set(category_ids)
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('home')
    
    categories = ServiceCategory.objects.all()
    
    return render(request, 'profile/provider_profile.html', {
        'provider': provider,
        'categories': categories,
    })

# ===== COMPATIBILITY FUNCTIONS (for existing URLs) =====

def find_jobs(request):
    """Redirect service providers to available jobs"""
    if not request.user.is_authenticated:
        messages.info(request, 'Please login or register as a service provider to find jobs.')
        return redirect('custom_login')
    
    # Check if user is a service provider
    try:
        ServiceProvider.objects.get(user=request.user)
        return redirect('available_jobs')
    except ServiceProvider.DoesNotExist:
        messages.warning(request, 'You need to complete your service provider profile first.')
        return redirect('provider_profile')


