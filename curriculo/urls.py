# curriculo/urls.py

from django.contrib import admin
from django.urls import path, re_path
from resume_app import views
from django.shortcuts import render, redirect, get_object_or_404 # <-- ADICIONE 'redirect' AQUI

# Swagger / OpenAPI
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schema_view = get_schema_view(
    openapi.Info(
        title="Currículo API",
        default_version='v1',
        description="Documentação Swagger/OpenAPI para o projeto de Currículo.",
        contact=openapi.Contact(email="support@example.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # This new line makes the create_resume view the homepage
    path('', views.create_resume, name='home'), 
    
    # You can keep this if you want /create/ to also work, or remove it
    path('create/', views.create_resume, name='create_resume'),
    path('generate_pdf/<int:resume_id>/', views.generate_pdf, name='generate_pdf'), # <-- O 'name' é crucial

    # Swagger/OpenAPI endpoints
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]