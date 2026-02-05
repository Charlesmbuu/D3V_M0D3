from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [

    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('available-jobs/', views.available_jobs, name='available_jobs'),
    path('job/<int:job_id>/', views.job_detail, name='job_detail'),
    path('job/<int:job_id>/complete/', views.mark_job_complete, name='mark_job_complete'),
    path('job/<int:job_id>/confirm/', views.confirm_job_completion, name='confirm_job_completion'),


]
