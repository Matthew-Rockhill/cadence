from django.db import models

class Student(models.Model):
    student_first_name = models.CharField(max_length=100)
    student_last_name = models.CharField(max_length=100)
    student_mobile = models.CharField(max_length=20, null=True, blank=True)
    parent_first_name = models.CharField(max_length=100, null=True, blank=True)
    parent_last_name = models.CharField(max_length=100, null=True, blank=True)
    parent_mobile = models.CharField(max_length=20, null=True, blank=True)
    parent_email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.student_first_name} {self.student_last_name}"