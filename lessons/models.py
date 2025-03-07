from django.db import models
from students.models import Student

class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson_date = models.DateField()
    duration = models.DecimalField(max_digits=3, decimal_places=1, default=1.0, 
                                help_text="Duration in hours (e.g., 0.5 for 30 minutes, 1.0 for 1 hour)")
    custom_rate = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True,
                                    help_text="Leave blank to use student's default rate")
    
    def __str__(self):
        return f"{self.student} - {self.lesson_date} ({self.duration}h)"
    
    def get_rate(self):
        """Returns the effective rate for this lesson"""
        if self.custom_rate:
            return self.custom_rate
        return 350.0  # Default rate - should be configurable or pulled from student profile
    
    def get_cost(self):
        """Calculate the cost for this lesson based on duration and rate"""
        return self.get_rate() * self.duration
