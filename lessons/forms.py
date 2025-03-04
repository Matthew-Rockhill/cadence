from django import forms
from .models import Lesson
from students.models import Student

class LessonForm(forms.ModelForm):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), empty_label="Select a student")

    class Meta:
        model = Lesson
        fields = ['student', 'lesson_date']
        widgets = {
            'lesson_date': forms.DateInput(attrs={'type': 'date'}),
        }

class BulkLessonForm(forms.Form):
    student = forms.ModelChoiceField(queryset=Student.objects.all(), empty_label="Select a student")
    dates = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'Enter dates one per line, e.g., 2025-03-01'}), help_text="Enter one date per line in YYYY-MM-DD format.")