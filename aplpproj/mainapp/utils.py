from django.shortcuts import redirect
from django.utils import timezone
from .models import UserSubscription

def subscription_required(view_func):
    def wrapper(request, *args, **kwargs):
        user_subscription = UserSubscription.objects.filter(user=request.user).first()

        if not user_subscription or not user_subscription.is_active():
            return redirect('mainapp:renew_subscription')  # Redirect if no active plan

        return view_func(request, *args, **kwargs)
    
    return wrapper
