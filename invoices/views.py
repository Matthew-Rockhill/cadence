from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from io import BytesIO
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Invoice
from lessons.models import Lesson
from students.models import Student  # Added missing import
from django.contrib import messages
from django.core.mail import EmailMessage
from django.conf import settings
import logging


logger = logging.getLogger(__name__)

@login_required
def generate_pdf_invoice(request, invoice_id):
    """
    Generate a PDF invoice for download
    """
    try:
        # Get the invoice
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        
        # Get lessons for this invoice
        lessons = Lesson.objects.filter(
            student=invoice.student,
            lesson_date__startswith=invoice.month
        ).order_by('lesson_date')
        
        # Prepare context
        context = {
            'invoice': invoice,
            'lessons': lessons,
            'year_month': invoice.month,
        }
        
        # Render template
        template = get_template('invoice_pdf.html')
        html = template.render(context)
        
        # Create PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            # Generate filename
            filename = f"Invoice_{invoice.student.student_last_name}_{invoice.month}.pdf"
            
            # Create HTTP response with PDF
            response = HttpResponse(result.getvalue(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        
        # If PDF generation failed
        logger.error(f"Error generating PDF for invoice {invoice_id}: PDF creation error")
        messages.error(request, "Error generating PDF invoice.")
        return redirect('generate_invoice', year_month=invoice.month)
    
    except Exception as e:
        logger.error(f"Error generating PDF for invoice {invoice_id}: {str(e)}")
        messages.error(request, f"Error generating PDF invoice: {str(e)}")
        return redirect('dashboard')

@login_required
def email_invoice(request, invoice_id):
    """
    Email an invoice to the student's parent
    """
    try:
        # Get the invoice
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        
        # Check if student has parent email
        if not invoice.student.parent_email:
            messages.error(request, f"Cannot send email: {invoice.student.student_first_name} {invoice.student.student_last_name} does not have a parent email specified.")
            logger.error(f"Email invoice failed: No parent email for student {invoice.student.student_first_name} {invoice.student.student_last_name}")
            return redirect('generate_invoice', year_month=invoice.month)
        
        # Get lessons for this invoice
        lessons = Lesson.objects.filter(
            student=invoice.student,
            lesson_date__startswith=invoice.month
        ).order_by('lesson_date')
        
        # Prepare context
        context = {
            'invoice': invoice,
            'lessons': lessons,
            'year_month': invoice.month,
        }
        
        # Render template
        template = get_template('invoice_pdf.html')
        html = template.render(context)
        
        # Create PDF
        result = BytesIO()
        pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
        
        if not pdf.err:
            # Generate filename
            filename = f"Invoice_{invoice.student.student_last_name}_{invoice.month}.pdf"
            
            # Create email
            subject = f"Cadence Tutoring Invoice - {invoice.month}"
            message = f"""
Dear {invoice.student.parent_first_name or 'Parent'},

Please find attached the invoice for {invoice.student.student_first_name}'s tutoring sessions for {invoice.month}.

Invoice Summary:
- Number of lessons: {invoice.lessons}
- Rate per lesson: R{invoice.rate_per_lesson}
- Total amount due: R{invoice.total_amount}

Payment Details:
- Bank: Standard Bank
- Account: 123456789
- Reference: {invoice.student.student_last_name}_{invoice.month}

Payment is due within 14 days of receipt.

Thank you for choosing Cadence Tutoring.

Best regards,
Cadence Tutoring
            """
            
            # Create the email
            email = EmailMessage(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [invoice.student.parent_email]
            )
            
            # Attach the PDF
            email.attach(filename, result.getvalue(), 'application/pdf')
            
            # Send the email
            email.send()
            
            # Log and redirect
            messages.success(request, f"Invoice emailed to {invoice.student.parent_email} successfully!")
            logger.info(f"Invoice emailed to {invoice.student.parent_email} for student {invoice.student.student_first_name} {invoice.student.student_last_name}")
            return redirect('generate_invoice', year_month=invoice.month)
        
        else:
            # PDF generation failed
            logger.error(f"Error emailing invoice {invoice_id}: PDF creation error")
            messages.error(request, "Error creating PDF for email attachment.")
            return redirect('generate_invoice', year_month=invoice.month)
            
    except Exception as e:
        logger.error(f"Error emailing invoice {invoice_id}: {str(e)}")
        messages.error(request, f"Error emailing invoice: {str(e)}")
        return redirect('generate_invoice', year_month=invoice.month)

@login_required
def generate_invoice(request, year_month):
    """
    Generate or display invoice for a specific month
    """
    try:
        # Default to current month if year_month is empty
        if not year_month:
            from datetime import datetime
            year_month = datetime.now().strftime('%Y-%m')
            
        # Get invoices for the specified month
        invoices = Invoice.objects.filter(month=year_month)
        lessons = Lesson.objects.filter(lesson_date__startswith=year_month)
        
        # Create default invoices for all students with 0 lessons if none exist
        if not invoices.exists():
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
        messages.error(request, f'There was an error generating the invoice: {str(e)}')
        return redirect('dashboard')

@login_required
def dashboard(request):
    """
    Enhanced dashboard with better data organization
    """
    # Import these within the function to avoid circular imports
    from datetime import datetime, timedelta
    from django.db.models import Q
    
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
    recent_invoices = Invoice.objects.filter(
        Q(month=three_months[0]) | Q(month=three_months[1]) | Q(month=three_months[2])
    ).order_by('-month', 'student__student_last_name')
    
    # All invoices for reference
    all_invoices = Invoice.objects.all().order_by('-month', 'student__student_last_name')
    
    context = {
        'students': students,
        'recent_lessons': recent_lessons,
        'all_lessons': all_lessons,
        'recent_invoices': recent_invoices,
        'all_invoices': all_invoices,
        'lessons': all_lessons,  # For backward compatibility
        'invoices': all_invoices,  # For backward compatibility
        'current_year_month': current_year_month,  # Ensure this is always set
    }
    
    return render(request, 'dashboard.html', context)

