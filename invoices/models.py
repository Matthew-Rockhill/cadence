from django.db import models
from students.models import Student

class Invoice(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    month = models.CharField(max_length=7, default='2025-01')  # Default to January 2025 as a placeholder (adjust as needed)
    lessons = models.IntegerField(default=0)
    rate_per_lesson = models.DecimalField(max_digits=6, decimal_places=2, default=350.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('student', 'month')  # Ensure one invoice per student per month

    def __str__(self):
        return f"Invoice for {self.student.student_first_name} {self.student.student_last_name} - {self.month} - R{self.total_amount}"

    def save(self, *args, **kwargs):
        if self.lessons < 0:
            self.lessons = 0
            self.total_amount = 0.00
        else:
            self.total_amount = self.lessons * self.rate_per_lesson
        super().save(*args, **kwargs)