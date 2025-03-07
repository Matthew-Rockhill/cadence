from django import forms
from .models import Lesson
from students.models import Student

class LessonForm(forms.ModelForm):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all().order_by('student_last_name', 'student_first_name'),
        empty_label="Select a student",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        })
    )

    class Meta:
        model = Lesson
        fields = ['student', 'lesson_date']
        widgets = {
            'lesson_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
        }

class BulkLessonForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=Student.objects.all().order_by('student_last_name', 'student_first_name'),
        empty_label="Select a student",
        widget=forms.Select(attrs={
            'class': 'mt-1 block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm'
        })
    )
    
    dates = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 5,
            'placeholder': 'Enter dates one per line, e.g., 2025-03-01',
            'class': 'shadow-sm focus:ring-indigo-500 focus:border-indigo-500 mt-1 block w-full sm:text-sm border border-gray-300 rounded-md'
        }),
        help_text="Enter one date per line in YYYY-MM-DD format."
    )