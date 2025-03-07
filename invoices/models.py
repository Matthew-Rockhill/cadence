from django.db import models
from students.models import Student

class Invoice(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('final', 'Final'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.CharField(max_length=7, default='2025-01')  # YYYY-MM format
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    lessons = models.IntegerField(default=0)
    rate_per_lesson = models.DecimalField(max_digits=6, decimal_places=2, default=350.0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    
    class Meta:
        unique_together = ('student', 'month', 'status')
    
    def __str__(self):
        return f"{self.student} - {self.month} - R{self.total_amount} ({self.status})"
    
    def finalize(self):
        """Convert a draft invoice to final"""
        if self.status == 'draft':
            # Check for existing final invoice for this month
            existing = Invoice.objects.filter(student=self.student, month=self.month, status='final').first()
            if existing:
                return False, "A finalised invoice already exists for this period"
            
            # Create a new final invoice
            final_invoice = Invoice.objects.create(
                student=self.student,
                month=self.month,
                start_date=self.start_date,
                end_date=self.end_date,
                lessons=self.lessons,
                rate_per_lesson=self.rate_per_lesson,
                total_amount=self.total_amount,
                status='final'
            )
            return True, final_invoice
        return False, "Invoice is already finalised"