from django.urls import path
from . import views

urlpatterns = [
    path('<str:year_month>/', views.generate_invoice, name='generate_invoice'),
    path('dashboard/', views.dashboard, name='dashboard'),
]