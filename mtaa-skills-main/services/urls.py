from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    
    path('', views.service_list, name='service_list'),
    path('create/', views.service_create, name='service_create'),
    path('<int:pk>/', views.service_detail, name='service_detail'),
    path('become-provider/', views.become_provider, name='become_provider'),
    path('provider-dashboard/', views.provider_dashboard, name='provider_dashboard'),
    path('providers/<int:provider_id>/', views.provider_detail, name='provider_detail'),

]