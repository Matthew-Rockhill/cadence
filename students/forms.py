from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['student_first_name', 'student_last_name', 'student_mobile', 'parent_first_name', 'parent_last_name', 'parent_mobile', 'parent_email']