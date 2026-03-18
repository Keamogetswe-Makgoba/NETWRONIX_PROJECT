from django.db import models
from django.conf import settings


class Question(models.Model):
    GRADE_CHOICES = [('11', 'Grade 11'), ('12', 'Grade 12')]
    
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    topic = models.CharField(max_length=100) 
    text = models.TextField()
    
   
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    
  
    correct_answer = models.CharField(max_length=1) 

    def __str__(self):
        return f"({self.grade}) {self.topic}: {self.text[:30]}..."
    
    

class QuizResult(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    grade = models.CharField(max_length=10) 
    topic = models.CharField(max_length=255, default="General")
    score = models.IntegerField()
    total_questions = models.IntegerField()
    percentage = models.FloatField()
    date_taken = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.username} - {self.score}/{self.total_questions}"
    

class LiveClass(models.Model):
    title = models.CharField(max_length=200)
    topic = models.CharField(max_length=100)
    grade = models.CharField(max_length=2, choices=[('11', '11'), ('12', '12')])
    meeting_id = models.CharField(max_length=100, unique=True, help_text="A unique name for the room")
    is_live = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} (Grade {self.grade})"