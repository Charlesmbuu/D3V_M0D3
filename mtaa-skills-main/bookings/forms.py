from django import forms
from .models import Job, Booking

class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['service_category', 'title', 'description', 'budget', 'location', 'preferred_date']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe what you need done...'}),
            'preferred_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['preferred_date'].required = False

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['agreed_price', 'scheduled_date', 'provider_message']
        widgets = {
            'scheduled_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'provider_message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Optional message to the customer...'}),
        }

