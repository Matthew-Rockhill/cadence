from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Lesson
from .forms import LessonForm, BulkLessonForm
from students.models import Student
from django.contrib import messages
import logging
from datetime import datetime
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
            # Update or create invoice for the month
            year_month = lesson.lesson_date.strftime('%Y-%m')
            update_or_create_invoice(lesson.student, year_month)
            return redirect('lessons')
        else:
            logger.error('Lesson form invalid: ' + str(form.errors))
            messages.error(request, 'There was an error logging the lesson.')
    else:
        form = LessonForm()
    students = Student.objects.all()
    return render(request, 'lessons.html', {'form': form, 'students': students})

@login_required
def bulk_log_lessons(request):
    if request.method == 'POST':
        form = BulkLessonForm(request.POST)
        if form.is_valid():
            student = form.cleaned_data['student']
            dates = form.cleaned_data['dates'].splitlines()  # Split by newline
            for date_str in dates:
                if date_str.strip():  # Ensure non-empty
                    try:
                        date = datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
                        Lesson.objects.create(student=student, lesson_date=date)
                    except ValueError:
                        messages.error(request, f'Invalid date format in "{date_str}". Use YYYY-MM-DD.')
                        logger.error(f'Invalid date format in bulk lesson log: {date_str}')
            messages.success(request, f'Bulk lessons logged successfully for {student.student_first_name} {student.student_last_name}!')
            logger.info(f'Bulk lessons logged for student {student.student_first_name} {student.student_last_name}.')
            year_month = dates[0].split('-')[0] + '-' + dates[0].split('-')[1] if dates else datetime.now().strftime('%Y-%m')
            update_or_create_invoice(student, year_month)
            return redirect('lessons')
        else:
            logger.error('Bulk lesson form invalid: ' + str(form.errors))
            messages.error(request, 'There was an error logging bulk lessons.')
    students = Student.objects.all()
    return render(request, 'lessons.html', {'students': students})

@login_required
def lesson_list(request):
    lessons = Lesson.objects.all()
    return render(request, 'lessons.html', {'lessons': lessons})

def update_or_create_invoice(student, year_month):
    try:
        # Get or create an invoice for this student and month
        invoice, created = Invoice.objects.get_or_create(
            student=student,
            month=year_month,
            defaults={'lessons': 0, 'total_amount': 0.00}
        )
        # Count lessons for this student in the specified month
        lessons = Lesson.objects.filter(student=student, lesson_date__startswith=year_month)
        invoice.lessons = lessons.count()
        invoice.total_amount = invoice.lessons * invoice.rate_per_lesson
        invoice.save()
        logger.info(f'Updated or created invoice for {student.student_first_name} {student.student_last_name} - {year_month} - R{invoice.total_amount}')
    except Exception as e:
        logger.error(f'Error updating/creating invoice for {student.student_first_name} {student.student_last_name} - {year_month}: {str(e)}')
        raise