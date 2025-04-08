from django.db import models
from django.core.validators import EmailValidator
from django.core.exceptions import ValidationError

def validate_email(value):
    validator = EmailValidator()
    try:
        validator(value)
    except ValidationError:
        raise ValidationError('Please enter a valid email address.')

class Student(models.Model):
    student_first_name = models.CharField(max_length=100)
    student_last_name = models.CharField(max_length=100)
    student_mobile = models.CharField(max_length=20, null=True, blank=True)
    parent_first_name = models.CharField(max_length=100, null=True, blank=True)
    parent_last_name = models.CharField(max_length=100, null=True, blank=True)
    parent_mobile = models.CharField(max_length=20, null=True, blank=True)
    parent_email = models.EmailField(
        max_length=254,
        validators=[validate_email],
        blank=True,
        null=True,
        help_text="Parent's email address for invoice delivery"
    )
    parent_phone = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.student_first_name} {self.student_last_name}"

    def clean(self):
        if self.parent_email:
            validate_email(self.parent_email)

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)