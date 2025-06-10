# models.py
from django.db import models
from django.contrib.auth.models import User

class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    managers = models.IntegerField(default=0)
    poltakers = models.IntegerField(default=0)
    surveys = models.IntegerField(default=0)
    contacts = models.IntegerField(default=0)

    def __str__(self):
        return self.name

from django.utils import timezone
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserSubscription(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    
    # ✅ Store Payment Proof
    payment_method = models.CharField(max_length=20, choices=[('paypal', 'PayPal'), ('stripe', 'Stripe')])
    transaction_id = models.CharField(max_length=255, unique=True, null=True, blank=True)  # ✅ PayPal Order ID / Stripe Payment Intent ID
    payment_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('completed', 'Completed'), ('failed', 'Failed')], default='pending')

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} ({self.payment_status})"

    def is_active(self):
        return self.expiration_date and timezone.now() < self.expiration_date


from django.db import models

class PaymentConfig(models.Model):
    PAYMENT_METHOD_CHOICES = (
        ('paypal', 'PayPal'),
        ('stripe', 'Stripe'),
    )
    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    client_id = models.CharField(max_length=255, blank=True, null=True)  # For PayPal
    client_secret = models.CharField(max_length=255, blank=True, null=True)  # For PayPal
    stripe_publishable_key = models.CharField(max_length=255, blank=True, null=True)  # For Stripe
    stripe_secret_key = models.CharField(max_length=255, blank=True, null=True)  # For Stripe
    
    def __str__(self):
        return f"Payment Config ({self.payment_method})"


