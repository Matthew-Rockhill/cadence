from datetime import datetime

def current_date_context(request):
    """
    Add current date information to all templates
    """
    now = datetime.now()
    current_year_month = now.strftime('%Y-%m')
    
    return {
        'current_year_month': current_year_month,
    }