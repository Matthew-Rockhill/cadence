from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generate/<str:year_month>/', views.generate_invoice, name='generate_invoice'),
]