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
        fields = ['student', 'lesson_date', 'duration', 'custom_rate']
        widgets = {
            'lesson_date': forms.DateInput(attrs={
                'type': 'date',
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md'
            }),
            'duration': forms.NumberInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md',
                'step': '0.5',
                'min': '0.5'
            }),
            'custom_rate': forms.NumberInput(attrs={
                'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md',
                'placeholder': 'Default rate will be used if blank'
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
        widget=forms.HiddenInput(attrs={
            'id': 'bulk_dates',
        }),
        required=True
    )
    
    duration = forms.DecimalField(
        initial=1.0,
        min_value=0.5,
        max_value=10,
        decimal_places=1,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md',
            'step': '0.5',
            'min': '0.5'
        }),
        help_text="Duration in hours for all selected dates"
    )
    
    custom_rate = forms.DecimalField(
        required=False,
        min_value=0,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md',
            'placeholder': 'Default rate will be used if blank'
        }),
        help_text="Custom rate for all selected dates (leave blank to use default)"
    )
