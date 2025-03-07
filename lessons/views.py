# lessons/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Lesson
from .forms import LessonForm, BulkLessonForm
from students.models import Student
from django.contrib import messages
import logging
from datetime import datetime
import json
from invoices.models import Invoice

logger = logging.getLogger(__name__)

@login_required
def log_lesson(request):
    if request.method == 'POST':
        form = LessonForm(request.POST)
        if form.is_valid():
            lesson = form.save()
            messages.success(request, f'Lesson for {lesson.student.student_first_name} {lesson.student.student_last_name} on {lesson.lesson_date} logged successfully!')
            logger.info(f'Lesson for student {lesson.student.student_first_name} {lesson.student.student_last_name} on {lesson.lesson_date} recorded.')
            # Update or create draft invoice for the month
            year_month = lesson.lesson_date.strftime('%Y-%m')
            update_or_create_invoice(lesson.student, year_month)
            return redirect('lessons')
        else:
            logger.error('Lesson form invalid: ' + str(form.errors))
            messages.error(request, 'There was an error logging the lesson.')
    else:
        form = LessonForm()
    
    # Get all students and lessons
    students = Student.objects.all().order_by('student_last_name', 'student_first_name')
    lessons = Lesson.objects.all().order_by('-lesson_date')
    bulk_form = BulkLessonForm()
    
    return render(request, 'lessons.html', {
        'form': form,
        'bulk_form': bulk_form,
        'students': students,
        'lessons': lessons
    })

@login_required
def bulk_log_lessons(request):
    if request.method == 'POST':
        form = BulkLessonForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            dates_json = form.cleaned_data['dates']
            duration = form.cleaned_data['duration']
            custom_rate = form.cleaned_data['custom_rate']
            
            try:
                # Parse dates from JSON array
                dates = json.loads(dates_json)
                
                if not dates:
                    messages.error(request, 'No dates selected. Please select at least one date.')
                    return redirect('lessons')
                
                # Create lessons for each date
                for date_str in dates:
                    try:
                        # Format from flatpickr is typically "YYYY-MM-DD"
                        date = datetime.strptime(date_str, '%Y-%m-%d').date()
                        
                        # Check if lesson already exists for this student and date
                        existing = Lesson.objects.filter(student=student, lesson_date=date).first()
                        if existing:
                            messages.warning(request, f'Lesson already exists for {date_str}. Skipping.')
                            continue
                            
                        # Create new lesson
                        Lesson.objects.create(
                            student=student, 
                            lesson_date=date,
                            duration=duration,
                            custom_rate=custom_rate
                        )
                    except ValueError:
                        messages.error(request, f'Invalid date format in "{date_str}". Skipping.')
                        logger.error(f'Invalid date format in bulk lesson log: {date_str}')
                
                messages.success(request, f'Bulk lessons logged successfully for {student.student_first_name} {student.student_last_name}!')
                logger.info(f'Bulk lessons logged for student {student.student_first_name} {student.student_last_name}.')
                
                # Update invoices for affected months
                if dates:
                    # Group dates by month and update invoices
                    months = set()
                    for date_str in dates:
                        try:
                            date = datetime.strptime(date_str, '%Y-%m-%d').date()
                            months.add(date.strftime('%Y-%m'))
                        except ValueError:
                            continue
                    
                    for month in months:
                        update_or_create_invoice(student, month)
            
            except json.JSONDecodeError:
                messages.error(request, 'Error processing selected dates.')
                logger.error('JSON decode error in bulk lesson form: ' + dates_json)
                
            return redirect('lessons')
        else:
            logger.error('Bulk lesson form invalid: ' + str(form.errors))
            messages.error(request, 'There was an error logging bulk lessons.')
    
    # Redirect to the main lessons page
    return redirect('lessons')

@login_required
def lesson_list(request):
    # Get all students and lessons
    students = Student.objects.all().order_by('student_last_name', 'student_first_name')
    lessons = Lesson.objects.all().order_by('-lesson_date')
    form = LessonForm()
    bulk_form = BulkLessonForm()
    
    return render(request, 'lessons.html', {
        'form': form,
        'bulk_form': bulk_form,
        'students': students,
        'lessons': lessons
    })

def update_or_create_invoice(student, year_month):
    try:
        # Get or create a draft invoice for this student and month
        invoice, created = Invoice.objects.get_or_create(
            student=student,
            month=year_month,
            status='draft',
            defaults={'lessons': 0, 'total_amount': 0.00}
        )
        
        # Calculate the date range for this month
        try:
            year, month = year_month.split('-')
            start_date = datetime.strptime(f'{year}-{month}-01', '%Y-%m-%d').date()
            
            # Find all lessons for this student in this month
            lessons = Lesson.objects.filter(
                student=student, 
                lesson_date__year=int(year),
                lesson_date__month=int(month)
            )
            
            # Update invoice details
            invoice.lessons = lessons.count()
            
            # Calculate total based on each lesson's duration and rate
            total = 0
            for lesson in lessons:
                if lesson.custom_rate:
                    total += lesson.duration * lesson.custom_rate
                else:
                    total += lesson.duration * invoice.rate_per_lesson
            
            invoice.total_amount = total
            
            # Set date range
            invoice.start_date = start_date
            if lessons.exists():
                invoice.end_date = lessons.latest('lesson_date').lesson_date
            
            invoice.save()
            
            logger.info(f'Updated draft invoice for {student.student_first_name} {student.student_last_name} - {year_month} - R{invoice.total_amount}')
            
        except ValueError:
            logger.error(f'Invalid month format: {year_month}')
            
    except Exception as e:
        logger.error(f'Error updating/creating invoice for {student.student_first_name} {student.student_last_name} - {year_month}: {str(e)}')
        raise
    
@login_required
def delete_lesson(request, pk):
    lesson = get_object_or_404(Lesson, pk=pk)
    student = lesson.student
    lesson_date = lesson.lesson_date
    year_month = lesson_date.strftime('%Y-%m')
    
    if request.method == 'POST':
        lesson.delete()
        messages.success(request, f'Lesson for {student.student_first_name} {student.student_last_name} on {lesson_date} deleted.')
        logger.info(f'Lesson for student {student.student_first_name} {student.student_last_name} on {lesson_date} deleted.')
        
        # Update the invoice
        update_or_create_invoice(student, year_month)
        
        # Redirect back to lessons page
        return redirect('lessons')
    
    return render(request, 'confirm_delete_lesson.html', {'lesson': lesson})