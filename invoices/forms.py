from django import forms
from datetime import datetime
from dateutil.relativedelta import relativedelta

class InvoiceGenerationForm(forms.Form):
    PERIOD_CHOICES = [
        ('custom', 'Custom Date Range'),
        ('current_month', 'Current Month'),
        ('previous_month', 'Previous Month'),
    ]
    
    period_type = forms.ChoiceField(
        choices=PERIOD_CHOICES,
        initial='current_month',
        widget=forms.RadioSelect(attrs={
            'class': 'form-radio'
        })
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md',
            'id': 'invoice_start_date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'mt-1 focus:ring-indigo-500 focus:border-indigo-500 block w-full shadow-sm sm:text-sm border-gray-300 rounded-md',
            'id': 'invoice_end_date'
        })
    )
    
    def clean(self):
        cleaned_data = super().clean()
        period_type = cleaned_data.get('period_type')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Set default dates based on period type
        today = datetime.now().date()
        
        if period_type == 'current_month':
            # First day of current month to today
            first_day = today.replace(day=1)
            cleaned_data['start_date'] = first_day
            cleaned_data['end_date'] = today
            
        elif period_type == 'previous_month':
            # First to last day of previous month
            first_day_prev_month = (today.replace(day=1) - relativedelta(months=1))
            last_day_prev_month = today.replace(day=1) - relativedelta(days=1)
            cleaned_data['start_date'] = first_day_prev_month
            cleaned_data['end_date'] = last_day_prev_month
            
        elif period_type == 'custom':
            if not start_date or not end_date:
                raise forms.ValidationError("Both start and end dates are required for custom period")
            if start_date > end_date:
                raise forms.ValidationError("End date must be after start date")
        
        return cleaned_data

class FinalizeInvoiceForm(forms.Form):
    invoice_id = forms.IntegerField(widget=forms.HiddenInput())