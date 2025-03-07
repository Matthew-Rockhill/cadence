# invoices/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('list/', views.invoice_list, name='invoice_list'),
    path('generate/', views.generate_invoice, name='generate_invoice'),
    path('view/<int:invoice_id>/', views.view_invoice, name='view_invoice'),
    path('finalize/', views.finalize_invoice, name='finalize_invoice'),
    path('pdf/<int:invoice_id>/', views.generate_pdf_invoice, name='generate_pdf_invoice'),
    path('email/<int:invoice_id>/', views.email_invoice, name='email_invoice'),
]