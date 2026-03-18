from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


class User(AbstractUser):
    IS_TEACHER = 'teacher'
    GRADE_11 = 'grade11'
    GRADE_12 = 'grade12'
    
    ROLE_CHOICES = [
        (IS_TEACHER, 'Teacher'),
        (GRADE_11, 'Grade 11 Student'),
        (GRADE_12, 'Grade 12 Student'),
    ]
    
    
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=GRADE_11)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.username} ({self.role})"

class AdditionalWork(models.Model):
    GRADE_CHOICES = [('11', 'Grade 11'), ('12', 'Grade 12')]
    
    title = models.CharField(max_length=200)
    link = models.URLField()
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __clstr__(self):
        return f"{self.grade} - {self.title}"




class LiveClass(models.Model):
    title = models.CharField(max_length=255)
    grade = models.CharField(max_length=20)
    meeting_id = models.CharField(max_length=100, unique=True)
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.title} - {self.grade}"