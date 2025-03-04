from django import forms
from .models import Student

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'student_first_name', 
            'student_last_name', 
            'student_mobile',
            'parent_first_name', 
            'parent_last_name', 
            'parent_mobile',
            'parent_email'
        ]
        widgets = {
            'student_first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'student_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_mobile': forms.TextInput(attrs={'class': 'form-control'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }