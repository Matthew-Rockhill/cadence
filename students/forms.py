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
            'student_first_name': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'student_last_name': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'student_mobile': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'parent_first_name': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'parent_last_name': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'parent_mobile': forms.TextInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'parent_email': forms.EmailInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
        }