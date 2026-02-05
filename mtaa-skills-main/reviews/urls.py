from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('create/<int:booking_id>/', views.create_review, name='create_review'),
    path('booking/<int:booking_id>/review/', views.create_review, name='create_review'),
    path('provider/<int:provider_id>/reviews/', views.provider_reviews, name='provider_reviews'),
    path('api/provider/<int:provider_id>/stats/', views.provider_stats_api, name='provider_stats_api'),
]
