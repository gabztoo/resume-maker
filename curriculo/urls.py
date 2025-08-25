# curriculo/urls.py

from django.contrib import admin
from django.urls import path
from resume_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This new line makes the create_resume view the homepage
    path('', views.create_resume, name='home'), 
    
    # You can keep this if you want /create/ to also work, or remove it
    path('create/', views.create_resume, name='create_resume'),
    
    path('generate_pdf/<int:resume_id>/', views.generate_pdf, name='generate_pdf'),
]