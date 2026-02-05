# backend/decorators.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages

def customer_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if hasattr(request.user, 'serviceprovider'):
            messages.error(request, 'This feature is for customers only.')
            return redirect('provider_dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

def provider_required(view_func):
    @login_required
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'serviceprovider'):
            messages.error(request, 'This feature is for service providers only.')
            return redirect('become_provider')
        return view_func(request, *args, **kwargs)
    return wrapper