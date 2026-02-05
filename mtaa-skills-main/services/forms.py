from django import forms
from .models import ServiceProvider, ServiceCategory

class ServiceProviderForm(forms.ModelForm):
    service_categories = forms.ModelMultipleChoiceField(
        queryset=ServiceCategory.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = ServiceProvider
        fields = [
            'business_name', 
            'service_categories', 
            'description', 
            'hourly_rate',
            'experience_years',
            'location',
            'phone',
            'email',
            'profile_picture'
        ]
        widgets = {
            'service_categories': forms.CheckboxSelectMultiple,
            'description': forms.Textarea(attrs={'rows': 4}),
        }


