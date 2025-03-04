from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Student
from .forms import StudentForm
from django.contrib import messages  # Ensure this import is present
import logging

logger = logging.getLogger(__name__)

@login_required
def add_student(request):
    if request.method == 'POST':
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.save()
            messages.success(request, f'Student {student.student_first_name} {student.student_last_name} added successfully!')
            logger.info(f'Student {student.student_first_name} {student.student_last_name} added.')
            return redirect('students')
        else:
            logger.error('Student form invalid: ' + str(form.errors))
            messages.error(request, 'There was an error adding the student.')
    else:
        form = StudentForm()
    return render(request, 'students.html', {'form': form})

@login_required
def student_list(request):
    students = Student.objects.all()
    return render(request, 'students.html', {'students': students})