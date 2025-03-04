from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Invoice
from lessons.models import Lesson
from students.models import Student  # Added missing import
from django.contrib import messages
import logging

logger = logging.getLogger(__name__)

@login_required
def generate_invoice(request, year_month):
    try:
        invoices = Invoice.objects.filter(month=year_month)
        lessons = Lesson.objects.filter(lesson_date__startswith=year_month)
        if not invoices.exists():
            # Create default invoices for all students with 0 lessons
            for student in Student.objects.all():
                Invoice.objects.get_or_create(
                    student=student,
                    month=year_month,
                    defaults={'lessons': 0, 'total_amount': 0.00}
                )
            invoices = Invoice.objects.filter(month=year_month)
        messages.success(request, f'Invoices generated for {year_month}')
        logger.info(f'Invoices generated for {year_month}')
        return render(request, 'invoice.html', {'invoices': invoices, 'lessons': lessons, 'year_month': year_month})
    except Exception as e:
        logger.error(f'Error generating invoice for {year_month}: {str(e)}')
        messages.error(request, 'There was an error generating the invoice.')
        return redirect('dashboard')

@login_required
def dashboard(request):
    students = Student.objects.all()
    lessons = Lesson.objects.all()
    invoices = Invoice.objects.all()
    return render(request, 'dashboard.html', {'students': students, 'lessons': lessons, 'invoices': invoices})