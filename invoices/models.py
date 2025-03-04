from django.db import models
from students.models import Student

class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.CharField(max_length=7, default='2025-01')
    lessons = models.IntegerField(default=0)
    rate_per_lesson = models.DecimalField(max_digits=6, decimal_places=2, default=350.0)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('student', 'month')
    
    def __str__(self):
        return f"{self.student} - {self.month} - R{self.total_amount}"