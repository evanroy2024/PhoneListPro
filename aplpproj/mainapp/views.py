from django.shortcuts import render

# Create your views here.

from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.core.mail import send_mail
import random

from django.contrib.auth.decorators import login_required
from mainapp.utils import subscription_required



otp_storage = {}  # Temporary storage (use DB in production)

# @login_required
# @subscription_required
def home(request):
    return render(request, 'mainpage.html')  # Placeholder home page

from django.contrib.auth import login, authenticate
from django.contrib import messages
from plpapp.models import Poltaker

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.shortcuts import render, redirect
from plpapp.models import Poltaker

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # 🔐 Flush any existing session — clears all session data and logs out any user
        request.session.flush()

        # 🔍 First try regular user authentication
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('plpapp:dashboard')

        # 🔍 If regular user auth fails, try poltaker authentication
        try:
            poltaker = Poltaker.objects.get(name=username)
        except Poltaker.DoesNotExist:
            try:
                poltaker = Poltaker.objects.get(email=username)
            except Poltaker.DoesNotExist:
                poltaker = None

        if poltaker and poltaker.password == password:
            # Login the associated user
            login(request, poltaker.user)
            # Mark this session as poltaker
            request.session['poltaker_id'] = poltaker.id
            return redirect('poltakerapp:poltaker_dashboard')
        
        # ❌ If both logins fail
        messages.error(request, "Invalid username or password")

    return render(request, 'mainapp/login.html')

def register_view(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken")
        elif User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
        else:
            otp = random.randint(100000, 999999)
            otp_storage[email] = otp  # Store OTP temporarily

            # Send OTP via email
            subject = "Your OTP for Registration"
            message = f"Your OTP is: {otp}. Please enter it to complete registration."
            send_mail(subject, message, 'your-email@gmail.com', [email])

            # Store user data temporarily
            request.session['temp_user'] = {
                'username': username,
                'email': email,
                'password': password
            }
            return redirect('mainapp:otp_verify')  # ✅ Fixed NoReverseMatch issue
    return render(request, 'mainapp/register.html')

def otp_verify(request):
    if request.method == "POST":
        email = request.session.get('temp_user', {}).get('email')
        entered_otp = request.POST['otp']

        if email and otp_storage.get(email) == int(entered_otp):
            user_data = request.session.pop('temp_user', None)
            if user_data:
                User.objects.create_user(user_data['username'], user_data['email'], user_data['password'])
                messages.success(request, "Registration successful! You can log in now.")
                return redirect('mainapp:login')
        messages.error(request, "Invalid OTP, please try again.")
    return render(request, 'mainapp/otp_verify.html')


from django.contrib.auth import logout

def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('mainapp:login')  # Redirect to login page after logout

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.urls import reverse

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        user = User.objects.filter(email=email).first()

        if user:
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = request.build_absolute_uri(reverse('mainapp:reset_password', args=[uid, token]))

            # Send email
            subject = "Password Reset Request"
            message = render_to_string('mainapp/password_reset_email.html', {'reset_link': reset_link})
            send_mail(subject, message, 'your-email@gmail.com', [email])

            messages.success(request, "Password reset link sent to your email.")
            return redirect('mainapp:forgot_password')

        messages.error(request, "No user found with this email.")
    
    return render(request, "mainapp/forgot_password.html")

def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            new_password = request.POST.get("password")
            user.set_password(new_password)
            user.save()
            messages.success(request, "Password reset successful! You can log in now.")
            return redirect("mainapp:login")

        return render(request, "mainapp/reset_password.html", {"uidb64": uidb64, "token": token})

    messages.error(request, "Invalid or expired password reset link.")
    return redirect("mainapp:forgot_password")

# Starting of Patments here ------------------------------------------------------------------------------------------------
from django.shortcuts import render , get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import SubscriptionPlan, PaymentConfig, UserSubscription
from django.utils import timezone
from datetime import timedelta

@login_required
def subscription_plans(request):
    plans = SubscriptionPlan.objects.all()
    payment_config = PaymentConfig.objects.first()  # Get the first available payment config
    
    return render(request, 'subscriptions/plans.html', {
        'plans': plans,
        'payment_method': payment_config.payment_method if payment_config else None,
        'stripe_key': payment_config.stripe_publishable_key if payment_config else None,
        'paypal_client_id': payment_config.client_id if payment_config else None,
    })


import stripe
from django.conf import settings
from django.http import JsonResponse

import stripe
import requests
from django.conf import settings
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from .models import SubscriptionPlan, UserSubscription, PaymentConfig

import stripe
import requests
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from .models import PaymentConfig, SubscriptionPlan, UserSubscription

@login_required
def checkout(request, plan_id):
    payment_config = PaymentConfig.objects.first()
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)

    if not payment_config:
        return JsonResponse({'error': 'Payment configuration not found'}, status=400)

    # ✅ Multiply price by 12
    final_price = plan.price * 12  

    if payment_config.payment_method == 'stripe':
        # ✅ Stripe Checkout
        stripe.api_key = payment_config.stripe_secret_key
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',  # ✅ Keep currency as USD
                    'product_data': {'name': plan.name},
                    'unit_amount': int(final_price * 100),  # ✅ 12x Price Applied
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(f"/stripe-success/{plan.id}/"),
            cancel_url=request.build_absolute_uri("/plans/"),
        )
        return redirect(session.url)

    elif payment_config.payment_method == 'paypal':
        # ✅ PayPal Checkout
        PAYPAL_CLIENT_ID = payment_config.client_id
        PAYPAL_CLIENT_SECRET = payment_config.client_secret

        # Get access token
        auth_response = requests.post(
            "https://api-m.sandbox.paypal.com/v1/oauth2/token",
            auth=(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET),
            data={"grant_type": "client_credentials"},
        )

        if auth_response.status_code != 200:
            print("🚨 PayPal Auth Error:", auth_response.json())  # Debugging
            return JsonResponse({'error': 'Failed to authenticate with PayPal', 'details': auth_response.json()}, status=400)

        access_token = auth_response.json().get("access_token")

        # Create order with 12x price
        order_payload = {
            "intent": "CAPTURE",
            "purchase_units": [{
                "amount": {"currency_code": "USD", "value": str(final_price)},  # ✅ 12x Price Applied
            }],
            "application_context": {
                "return_url": request.build_absolute_uri(f"/paypal-success/{plan.id}/"),
                "cancel_url": request.build_absolute_uri("/plans/"),
            }
        }

        order_response = requests.post(
            "https://api-m.sandbox.paypal.com/v2/checkout/orders",
            headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
            json=order_payload,
        )

        if order_response.status_code != 201:
            print("🚨 PayPal Order Error:", order_response.json())  # Debugging
            return JsonResponse({'error': 'Failed to create PayPal order', 'details': order_response.json()}, status=400)

        approval_url = next(link["href"] for link in order_response.json()["links"] if link["rel"] == "approve")
        return redirect(approval_url)

    return JsonResponse({'error': 'Invalid payment method selected'}, status=400)

@login_required
def stripe_success(request, plan_id):
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    stripe_payment_intent = request.GET.get("payment_intent")  # ✅ Get Stripe Payment Intent ID

    user_subscription, created = UserSubscription.objects.get_or_create(user=request.user)
    user_subscription.plan = plan
    user_subscription.start_date = timezone.now()
    user_subscription.expiration_date = timezone.now() + timedelta(days=30)
    user_subscription.payment_method = 'stripe'  # ✅ Store Payment Method
    user_subscription.transaction_id = stripe_payment_intent  # ✅ Store Payment ID
    user_subscription.payment_status = 'completed'
    user_subscription.save()

    return redirect('home')  # Redirect to home after payment

import requests
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from datetime import timedelta
from django.http import JsonResponse
from .models import UserSubscription, SubscriptionPlan, PaymentConfig

@login_required
def paypal_success(request, plan_id):
    token = request.GET.get("token")  # ✅ PayPal sends token after approval
    if not token:
        return JsonResponse({'error': 'Missing PayPal token'}, status=400)

    payment_config = PaymentConfig.objects.first()
    if not payment_config:
        return JsonResponse({'error': 'Payment configuration not found'}, status=400)

    # ✅ Get PayPal Access Token Again
    auth_response = requests.post(
        "https://api-m.sandbox.paypal.com/v1/oauth2/token",
        auth=(payment_config.client_id, payment_config.client_secret),
        data={"grant_type": "client_credentials"},
    )

    if auth_response.status_code != 200:
        return JsonResponse({'error': 'Failed to authenticate with PayPal', 'details': auth_response.json()}, status=400)

    access_token = auth_response.json().get("access_token")

    # ✅ Capture Payment
    capture_response = requests.post(
        f"https://api-m.sandbox.paypal.com/v2/checkout/orders/{token}/capture",
        headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
    )

    if capture_response.status_code != 201:
        return JsonResponse({'error': 'Failed to capture PayPal payment', 'details': capture_response.json()}, status=400)

    # ✅ Extract PayPal Transaction ID
    capture_data = capture_response.json()
    transaction_id = capture_data["purchase_units"][0]["payments"]["captures"][0]["id"]

    # ✅ Payment Captured Successfully → Activate Subscription
    plan = get_object_or_404(SubscriptionPlan, id=plan_id)
    user_subscription, created = UserSubscription.objects.get_or_create(user=request.user)
    user_subscription.plan = plan
    user_subscription.start_date = timezone.now()
    user_subscription.expiration_date = timezone.now() + timedelta(days=30)
    user_subscription.payment_method = 'paypal'  # ✅ Store Payment Method
    user_subscription.transaction_id = transaction_id  # ✅ Store PayPal Transaction ID
    user_subscription.payment_status = 'completed'
    user_subscription.save()

    return redirect('mainapp:home')  # Redirect to homepage

from django.shortcuts import render

def renew_subscription(request):
    return render(request, 'subscriptions/renew_subscription.html')
# Ending of Patments here ------------------------------------------------------------------------------------------------


def mainpage(request):
    return render(request , 'mainpage/index.html')