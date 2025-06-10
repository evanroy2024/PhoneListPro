from django.db import models

# Create your models here.
# models.py
from django.db import models
from django.contrib.auth.models import User

class Question(models.Model):
    QUESTION_TYPES = (
        ('mcq', 'Multiple Choice'),
        ('text', 'Open Text'),
        ('yesno', 'Yes/No'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question_text = models.CharField(max_length=255)
    question_type = models.CharField(max_length=10, choices=QUESTION_TYPES)
    
    def __str__(self):
        return self.question_text

class Option(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    option_text = models.CharField(max_length=255)

    def __str__(self):
        return self.option_text



# For contacts ----------------------------- 

class UserContactList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    street = models.CharField(max_length=255, blank=True, default='NA')
    city = models.CharField(max_length=100, blank=True, default='NA')
    state = models.CharField(max_length=100, blank=True, default='NA')
    country = models.CharField(max_length=100, blank=True, default='NA')
    zipcode = models.CharField(max_length=20, blank=True, default='NA')  # Updated to CharField
    party_preference = models.CharField(max_length=50, choices=[
        ('Republican', 'Republican'),
        ('Democrat', 'Democrat'),
        ('Independent', 'Independent'),
        ('NA', 'NA'),  # Added 'NA' as a choice
    ], blank=True, default='NA')

    # New fields added with `null=True` and `blank=True`
    state_id = models.CharField(max_length=50, null=True, blank=True, default='NA')
    voter_nbr = models.CharField(max_length=50, null=True, blank=True, default='NA')
    title = models.CharField(max_length=50, null=True, blank=True, default='NA')
    address = models.CharField(max_length=255, null=True, blank=True, default='NA')
    address2 = models.CharField(max_length=255, null=True, blank=True, default='NA')
    phone = models.CharField(max_length=15, null=True, blank=True, default='NA')
    dob = models.DateField(null=True, blank=True)
    reg_date = models.DateField(null=True, blank=True)
    district = models.CharField(max_length=50, null=True, blank=True, default='NA')
    pct_nbr = models.CharField(max_length=50, null=True, blank=True, default='NA')
    ward = models.CharField(max_length=50, null=True, blank=True, default='NA')
    # New 'status' field added
    status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('denied', 'Denied')],default='pending' )
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.email}"

# Poltaker -------------------------------------------------------------------- 
class Poltaker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poltakers")
    name = models.CharField(max_length=100)
    mobile = models.CharField(max_length=50 , default="0")
    email = models.EmailField(unique=True)
    zip_code = models.CharField(max_length=100 , default="0")

    Street = models.CharField(max_length=100,default='0')
    city = models.CharField(max_length=100,default='0')
    state = models.CharField(max_length=100,default='0')
    password = models.CharField(max_length=128)   
    # New fields for tracking survey statuses
    completed_surveys = models.IntegerField(default=0)
    inprogress_surveys = models.IntegerField(default=0)
    pending_surveys = models.IntegerField(default=0)
    total_survey = models.IntegerField(default=0)
    password_changed = models.BooleanField(default=False)  # Add this field
    password_reset_token = models.CharField(max_length=256, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} (Poltaker for {self.user.username})"
    

# User Profile 

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True, default='NA')
    street = models.CharField(max_length=255, blank=True, default='NA')
    city = models.CharField(max_length=100, blank=True, default='NA')
    state = models.CharField(max_length=100, blank=True, default='NA')
    zipcode = models.CharField(max_length=20, blank=True, default='NA')
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f'{self.user.username} Profile'



class Notification(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject
    

from django.db import models

class AppNotifications(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='notifications/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

from django.db import models
from django.contrib.auth.models import User

class HelpRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.subject}"

from django.db import models
from django.contrib.auth.models import User

class UserSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='settings')

    # Notification Preferences
    email_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=False)
    marketing_emails = models.BooleanField(default=False)

    # Privacy Settings
    PROFILE_VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    profile_visibility = models.CharField(max_length=7, choices=PROFILE_VISIBILITY_CHOICES, default='private')

    DATA_COLLECTION_CHOICES = [
        ('allow', 'Allow'),
        ('deny', 'Deny'),
    ]
    data_collection = models.CharField(max_length=5, choices=DATA_COLLECTION_CHOICES, default='deny')

    TWO_FACTOR_CHOICES = [
        ('enabled', 'Enabled'),
        ('disabled', 'Disabled'),
    ]
    two_factor = models.CharField(max_length=8, choices=TWO_FACTOR_CHOICES, default='disabled')

    def __str__(self):
        return f"Settings for {self.user.username}"
