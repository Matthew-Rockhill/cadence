from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('generate/<str:year_month>/', views.generate_invoice, name='generate_invoice'),
    path('pdf/<int:invoice_id>/', views.generate_pdf_invoice, name='generate_pdf_invoice'),
    path('email/<int:invoice_id>/', views.email_invoice, name='email_invoice'),
]