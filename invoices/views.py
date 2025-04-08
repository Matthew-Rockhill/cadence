# invoices/views.py
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Invoice
from .forms import InvoiceGenerationForm, FinalizeInvoiceForm
from lessons.models import Lesson
from students.models import Student 
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
import logging
from datetime import datetime
import time
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

logger = logging.getLogger(__name__)

def generate_pdf_content(html_content):
    """Generate PDF content from HTML with proper error handling"""
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html_content.encode("UTF-8")), result)
    
    if pdf.err:
        raise Exception(f"PDF generation failed: {pdf.err}")
    
    return result.getvalue()

def save_pdf_backup(pdf_content, invoice):
    """Save PDF backup to storage"""
    filename = f"invoices/backup_{invoice.id}_{invoice.month}.pdf"
    try:
        default_storage.save(filename, ContentFile(pdf_content))
        return filename
    except Exception as e:
        logger.error(f"Failed to save PDF backup: {str(e)}")
        return None

@login_required
def generate_pdf_invoice(request, invoice_id):
    """Generate a PDF invoice for download with improved error handling"""
    try:
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        lessons = get_lessons_for_invoice(invoice)
        
        context = {
            'invoice': invoice,
            'lessons': lessons,
            'year_month': invoice.month,
        }
        
        template = get_template('invoice_pdf.html')
        html = template.render(context)
        
        # Generate PDF with proper error handling
        pdf_content = generate_pdf_content(html)
        
        # Save backup
        backup_path = save_pdf_backup(pdf_content, invoice)
        if backup_path:
            logger.info(f"PDF backup saved: {backup_path}")
        
        # Generate filename
        filename = f"Invoice_{invoice.student.student_last_name}_{invoice.month}.pdf"
        
        # Create HTTP response with PDF
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    
    except Exception as e:
        logger.error(f"Error generating PDF for invoice {invoice_id}: {str(e)}")
        messages.error(request, "We encountered an error generating your invoice. Please try again or contact support.")
        return redirect('dashboard')

def send_email_with_retry(email_message, max_retries=3, delay=1):
    """Send email with retry mechanism"""
    for attempt in range(max_retries):
        try:
            email_message.send()
            return True
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            logger.warning(f"Email send attempt {attempt + 1} failed: {str(e)}")
            time.sleep(delay * (attempt + 1))  # Exponential backoff

@login_required
def email_invoice(request, invoice_id):
    """Email an invoice to the student's parent with improved error handling"""
    try:
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        
        if not invoice.student.parent_email:
            messages.error(
                request, 
                f"Cannot send email: {invoice.student.student_first_name} {invoice.student.student_last_name} does not have a parent email specified."
            )
            return redirect('view_invoice', invoice_id=invoice.id)
        
        # Generate PDF
        lessons = get_lessons_for_invoice(invoice)
        context = {
            'invoice': invoice,
            'lessons': lessons,
            'year_month': invoice.month,
        }
        
        template = get_template('invoice_pdf.html')
        html = template.render(context)
        pdf_content = generate_pdf_content(html)
        
        # Save backup
        backup_path = save_pdf_backup(pdf_content, invoice)
        
        # Prepare email
        email = EmailMessage(
            subject=f'Invoice for {invoice.month} - {invoice.student.student_first_name} {invoice.student.student_last_name}',
            body=f'Please find attached the invoice for {invoice.month}.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[invoice.student.parent_email]
        )
        
        # Attach PDF
        filename = f"Invoice_{invoice.student.student_last_name}_{invoice.month}.pdf"
        email.attach(filename, pdf_content, 'application/pdf')
        
        # Send email with retry
        send_email_with_retry(email)
        
        messages.success(request, f"Invoice has been sent to {invoice.student.parent_email}")
        return redirect('view_invoice', invoice_id=invoice.id)
        
    except Exception as e:
        logger.error(f"Error emailing invoice {invoice_id}: {str(e)}")
        messages.error(request, "We encountered an error sending your invoice. Please try again or contact support.")
        return redirect('view_invoice', invoice_id=invoice_id)

def get_lessons_for_invoice(invoice):
    """Helper function to get lessons for an invoice based on its date range or month"""
    if invoice.start_date and invoice.end_date:
        # If we have a date range, use that
        return Lesson.objects.filter(
            student=invoice.student,
            lesson_date__gte=invoice.start_date,
            lesson_date__lte=invoice.end_date
        ).order_by('lesson_date')
    else:
        # Otherwise use the month
        return Lesson.objects.filter(
            student=invoice.student,
            lesson_date__startswith=invoice.month
        ).order_by('lesson_date')

@login_required
def invoice_list(request):
    """
    Display list of all invoices, both draft and final
    """
    draft_invoices = Invoice.objects.filter(status='draft').order_by('-month', 'student__student_last_name')
    final_invoices = Invoice.objects.filter(status='final').order_by('-month', 'student__student_last_name')
    
    return render(request, 'invoice_list.html', {
        'draft_invoices': draft_invoices,
        'final_invoices': final_invoices,
    })

@login_required
def view_invoice(request, invoice_id):
    """
    View a single invoice with all its details
    """
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    lessons = get_lessons_for_invoice(invoice)
    finalize_form = FinalizeInvoiceForm(initial={'invoice_id': invoice.id})
    
    return render(request, 'view_invoice.html', {
        'invoice': invoice,
        'lessons': lessons,
        'finalize_form': finalize_form,
    })

@login_required
def generate_invoice(request):
    """
    Generate new invoices based on specific criteria
    """
    form = InvoiceGenerationForm(request.POST or None)
    
    if request.method == 'POST' and form.is_valid():
        period_type = form.cleaned_data['period_type']
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        
        try:
            # Determine the month string for the invoice (using the first date of the range)
            month_str = start_date.strftime('%Y-%m')
            
            # Find all students who had lessons in this period
            lessons_in_period = Lesson.objects.filter(
                lesson_date__gte=start_date,
                lesson_date__lte=end_date
            )
            
            students_with_lessons = set(lessons_in_period.values_list('student', flat=True))
            
            # Create or update invoices for each student
            for student_id in students_with_lessons:
                student = Student.objects.get(pk=student_id)
                
                # Check if draft invoice exists for this month and student
                invoice, created = Invoice.objects.get_or_create(
                    student=student,
                    month=month_str,
                    status='draft',
                    defaults={
                        'start_date': start_date,
                        'end_date': end_date,
                        'lessons': 0,
                        'total_amount': 0.00,
                        'rate_per_lesson': 350.00  # Default rate per lesson
                    }
                )
                
                # Find lessons for this student in this period
                student_lessons = lessons_in_period.filter(student=student)
                
                # Update invoice
                invoice.start_date = start_date
                invoice.end_date = end_date
                invoice.lessons = student_lessons.count()
                
                # Calculate total amount based on each lesson's duration and rate
                total = 0
                for lesson in student_lessons:
                    if lesson.custom_rate:
                        total += lesson.duration * lesson.custom_rate
                    else:
                        total += lesson.duration * invoice.rate_per_lesson
                
                invoice.total_amount = total
                invoice.save()
            
            messages.success(request, f'Invoices generated for period {start_date} to {end_date}')
            logger.info(f'Invoices generated for period {start_date} to {end_date}')
            return redirect('invoice_list')
                
        except Exception as e:
            logger.error(f'Error generating invoices: {str(e)}')
            messages.error(request, f'There was an error generating invoices: {str(e)}')
            return redirect('dashboard')
    
    return render(request, 'generate_invoice.html', {'form': form})

@login_required
def finalize_invoice(request):
    """
    Convert a draft invoice to final status
    """
    if request.method == 'POST':
        form = FinalizeInvoiceForm(request.POST)
        if form.is_valid():
            invoice_id = form.cleaned_data['invoice_id']
            invoice = get_object_or_404(Invoice, pk=invoice_id, status='draft')
            
            success, result = invoice.finalize()
            
            if success:
                messages.success(request, f'Invoice for {invoice.student.student_first_name} {invoice.student.student_last_name} has been finalized')
                return redirect('view_invoice', invoice_id=result.id)
            else:
                messages.error(request, f'Failed to finalize invoice: {result}')
                return redirect('view_invoice', invoice_id=invoice_id)
    
    # If we get here, something's wrong
    messages.error(request, 'Invalid request')
    return redirect('invoice_list')

@login_required
def dashboard(request):
    """
    Enhanced dashboard with better data organization
    """
    # Import these within the function to avoid circular imports
    from datetime import datetime, timedelta
    from django.db.models import Q, Sum
    
    # Get current date for default year-month
    current_date = datetime.now()
    current_year_month = current_date.strftime('%Y-%m')
    
    students = Student.objects.all().order_by('student_last_name', 'student_first_name')
    
    # Get recent lessons (last 30 days)
    thirty_days_ago = current_date.date() - timedelta(days=30)
    recent_lessons = Lesson.objects.filter(lesson_date__gte=thirty_days_ago).order_by('-lesson_date')
    
    # All lessons for reference
    all_lessons = Lesson.objects.all().order_by('-lesson_date')
    
    # Get recent invoices (last 3 months)
    current_month_num = int(current_date.strftime('%m'))
    current_year = int(current_date.strftime('%Y'))
    
    three_months = []
    for i in range(3):
        month_num = current_month_num - i
        year = current_year
        
        if month_num <= 0:
            month_num += 12
            year -= 1
            
        three_months.append(f"{year}-{month_num:02d}")
    
    # Query for invoices from the last three months
    recent_draft_invoices = Invoice.objects.filter(
        status='draft',
        month__in=three_months
    ).order_by('-month', 'student__student_last_name')
    
    recent_final_invoices = Invoice.objects.filter(
        status='final',
        month__in=three_months
    ).order_by('-month', 'student__student_last_name')
    
    # Calculate summary statistics
    total_draft_amount = Invoice.objects.filter(status='draft').aggregate(total=Sum('total_amount'))['total'] or 0
    total_final_amount = Invoice.objects.filter(status='final').aggregate(total=Sum('total_amount'))['total'] or 0
    total_lessons = Lesson.objects.count()
    
    context = {
        'students': students,
        'recent_lessons': recent_lessons,
        'all_lessons': all_lessons,
        'recent_draft_invoices': recent_draft_invoices,
        'recent_final_invoices': recent_final_invoices,
        'total_draft_amount': total_draft_amount,
        'total_final_amount': total_final_amount,
        'total_lessons': total_lessons,
        'current_year_month': current_year_month,
    }
    
    return render(request, 'dashboard.html', context)