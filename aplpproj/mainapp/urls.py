from django.urls import path
from .views import home 
from .views import login_view, register_view, otp_verify ,logout_view
from .views import subscription_plans
from .views import checkout, stripe_success, paypal_success ,renew_subscription
from .views import forgot_password, reset_password

app_name = 'mainapp'

urlpatterns = [
    path('', home, name='home'),
    path('login/', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('otp-verify/', otp_verify, name='otp_verify'),
    path('logout/', logout_view, name='logout'),  # ✅ Logout URL
    path("forgot-password/", forgot_password, name="forgot_password"),
    path("reset-password/<uidb64>/<token>/", reset_password, name="reset_password"),

    path('plans/', subscription_plans, name='subscription_plans'),
    path('checkout/<int:plan_id>/', checkout, name='checkout'),
    path('stripe-success/<int:plan_id>/', stripe_success, name='stripe_success'),
    path('paypal-success/<int:plan_id>/', paypal_success, name='paypal_success'),
    path('renew-subscription/', renew_subscription, name='renew_subscription'),

]
