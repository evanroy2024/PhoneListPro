from django.db import models
from django.contrib.auth.models import User
from plpapp.models import Poltaker, Question ,UserContactList
from django.utils import timezone

# Create your models here.
class Survey(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='surveys')
    polltaker = models.ForeignKey(Poltaker, on_delete=models.CASCADE, related_name="surveys")
    questions = models.ManyToManyField(Question, related_name="surveys")
    contacts = models.ManyToManyField(UserContactList, related_name='surveys')  # Add this line
    created_at = models.DateTimeField(auto_now_add=True)
    survey_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('in_progress', 'In Progress'), ('completed', 'Completed')], default='pending')
    # Here in progress means we say denied to show its denied not deleted from our DB 
    
    # Add the survey_token field to store the random token
    survey_token = models.CharField(max_length=15)  # Unique constraint here

class SurveyResponse(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE)
    polltaker = models.ForeignKey(Poltaker, on_delete=models.CASCADE)
    contact = models.ForeignKey(UserContactList, on_delete=models.CASCADE, null=True)
    responses = models.JSONField()  # Store responses as JSON
    submitted_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=True)  # New field to mark completion
    denial_reason = models.TextField(null=True, blank=True)  # New field for denial reason

    def __str__(self):
        return f"Response by {self.polltaker} for survey '{self.survey.title}'"

