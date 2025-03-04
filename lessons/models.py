from django.db import models
from students.models import Student

class Lesson(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    lesson_date = models.DateField()
    
    def __str__(self):
        return f"{self.student} - {self.lesson_date}"