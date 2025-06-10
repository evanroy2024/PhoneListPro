from django.shortcuts import render
from django.contrib.auth.decorators import login_required
# Create your views here.
@login_required
def dashboard(request):
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    surveys = Survey.objects.filter(created_by=request.user)
    
    if start_date and end_date:
        surveys = surveys.filter(survey_date__range=[start_date, end_date])
    
    # Calculate all the statistics
    total_surveys = surveys.count()
    completed_surveys = surveys.filter(status='completed').count()
    pending_surveys = surveys.filter(status='pending').count()
    denied_surveys = surveys.filter(status='in_progress').count()
    
    # Survey completion rate
    completion_rate = (completed_surveys / total_surveys) * 100 if total_surveys > 0 else 0
    
    # User's subscription details
    subscription = UserSubscription.objects.filter(user=request.user).first()
        
    context = {
        'user': request.user,
        'subscription': subscription,
        'surveys': surveys,
        'total_surveys': total_surveys,
        'completed_count': completed_surveys,
        'pending_count': pending_surveys,
        'denied_count': denied_surveys,
        'completion_rate': round(completion_rate, 2),
        'completion_percentage': round(completion_rate, 2),
        'start_date': start_date,
        'end_date': end_date
    }

    return render(request, 'analytics.html', context)

# views.py
import csv
import pandas as pd
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Question, Option
from django.contrib import messages
from django.core.files.storage import FileSystemStorage

# views.py (update this)
from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse
@login_required
@csrf_exempt
def upload_questions(request):
    if request.method == 'POST':
        # File upload handling (CSV or Excel)
        if request.FILES.get('file'):
            upload_file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(upload_file.name, upload_file)
            file_path = fs.path(filename)

            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

                for _, row in df.iterrows():
                    question_text = row.get('question_text')
                    question_type = row.get('question_type')
                    options = str(row.get('options')).split('|') if pd.notna(row.get('options')) else []

                    if question_text and question_type:
                        question = Question.objects.create(
                            user=request.user,
                            question_text=question_text,
                            question_type=question_type
                        )

                        if question_type == 'mcq' and options:
                            combined_options = ', '.join(opt.strip() for opt in options if opt.strip())
                            Option.objects.create(question=question, option_text=combined_options)

                messages.success(request, 'Questions uploaded successfully.')
            except Exception as e:
                messages.error(request, f"Error processing file: {e}")

        # Manual question submission (via JSON)
        elif request.headers.get('Content-Type') == 'application/json':
            try:
                data = json.loads(request.body)
                question_text = data.get('question_text')
                question_type = data.get('question_type')
                options = data.get('options', [])

                if question_text and question_type:
                    question = Question.objects.create(
                        user=request.user,
                        question_text=question_text,
                        question_type=question_type
                    )

                    if question_type == 'mcq' and options:
                        combined_options = ', '.join(opt.strip() for opt in options if opt.strip())
                        Option.objects.create(question=question, option_text=combined_options)

                    return JsonResponse({'success': True})
                else:
                    return JsonResponse({'success': False, 'error': 'Missing data'})
            except Exception as e:
                return JsonResponse({'success': False, 'error': str(e)})

    return render(request, 'plpapp/questions/upload_questions.html')


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Question
from django.http import JsonResponse

@login_required
def list_questions(request):
    if request.method == 'POST':
        # Handle delete action
        selected_ids = request.POST.getlist('selected_questions')
        if selected_ids:
            try:
                Question.objects.filter(id__in=selected_ids).delete()
                messages.success(request, 'Selected questions deleted successfully.')
            except Exception as e:
                messages.error(request, f"Error deleting questions: {e}")
        return redirect('plpapp:list_questions')  # Redirect to avoid re-submitting the form on refresh

    # Get all questions
    questions = Question.objects.filter(user=request.user)

    return render(request, 'plpapp/questions/list_questions.html', {'questions': questions})


# User Contact List starts Here ------------------------------------------------------------------------------------------------
import pandas as pd
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from .models import UserContactList

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.files.storage import FileSystemStorage
from datetime import datetime
import pandas as pd
from .models import UserContactList

def parse_date(date_str):
    """Try parsing a date string into a date object."""
    if not date_str or pd.isna(date_str):
        return None
    for fmt in ('%m/%d/%Y', '%m-%d-%Y', '%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(str(date_str), fmt).date()
        except Exception:
            continue
    return None

from django.views.decorators.csrf import csrf_exempt

@login_required
@csrf_exempt
def upload_user_contacts(request):
    if request.method == 'POST':
        if request.FILES.get('file'):
            upload_file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(upload_file.name, upload_file)
            file_path = fs.path(filename)

            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

                created_count = 0
                for _, row in df.iterrows():
                    first_name = row.get('FNAME') or row.get('first_name')
                    last_name = row.get('LNAME') or row.get('last_name')
                    email = row.get('EMAIL') or row.get('email')

                    if first_name and last_name and email:
                        UserContactList.objects.create(
                            user=request.user,
                            first_name=first_name,
                            last_name=last_name,
                            email=email,
                            street=row.get('ADDRESS', 'NA'),
                            city=row.get('CITY', 'NA'),
                            state=row.get('STATE', 'NA'),
                            country='NA',
                            zipcode=row.get('ZIP', 'NA'),
                            party_preference=row.get('party_preference', 'NA'),
                            state_id=row.get('STATE_ID', 'NA'),
                            voter_nbr=row.get('VOTER_NBR', 'NA'),
                            title=row.get('TITLE', 'NA'),
                            address=row.get('ADDRESS', 'NA'),
                            address2=row.get('ADDRESS2', 'NA'),
                            phone=row.get('PHONE', 'NA'),
                            dob=pd.to_datetime(row.get('DOB'), errors='coerce'),
                            reg_date=pd.to_datetime(row.get('REG_DATE'), errors='coerce'),
                            district=row.get('DISTRICT', 'NA'),
                            pct_nbr=row.get('PCT_NBR', 'NA'),
                            ward=row.get('WARD', 'NA'),
                            status='pending',
                        )
                        created_count += 1

                if created_count:
                    messages.success(request, f'{created_count} contacts uploaded successfully.')
                else:
                    messages.warning(request, 'No contacts were created. Please check your file content.')

            except Exception as e:
                messages.error(request, f"Error processing file: {e}")

        elif request.POST.get('manual_submit') == 'true':
            # Handle manual contact add from HTML
            first_name = request.POST.get('first_name')
            last_name = request.POST.get('last_name')
            email = request.POST.get('email')

            if first_name and last_name and email:
                UserContactList.objects.create(
                    user=request.user,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    street=request.POST.get('street', 'NA'),
                    city=request.POST.get('city', 'NA'),
                    state=request.POST.get('state', 'NA'),
                    country=request.POST.get('country', 'NA'),
                    zipcode=request.POST.get('zipcode', 'NA'),
                    party_preference=request.POST.get('party_preference', 'NA'),
                    state_id=request.POST.get('state_id', 'NA'),
                    voter_nbr=request.POST.get('voter_nbr', 'NA'),
                    title=request.POST.get('title', 'NA'),
                    address=request.POST.get('address', 'NA'),
                    address2=request.POST.get('address2', 'NA'),
                    phone=request.POST.get('phone', 'NA'),
                    dob=request.POST.get('dob') or None,
                    reg_date=request.POST.get('reg_date') or None,
                    district=request.POST.get('district', 'NA'),
                    pct_nbr=request.POST.get('pct_nbr', 'NA'),
                    ward=request.POST.get('ward', 'NA'),
                    status=request.POST.get('status', 'pending'),
                )
                messages.success(request, "Contact added manually.")
            else:
                messages.error(request, "First name, last name, and email are required.")

        return redirect('plpapp:list_user_contacts')

    return render(request, 'plpapp/contact/upload_user_contacts.html')

@login_required
def list_user_contacts(request):
    if request.method == 'POST':
        # Handle delete action
        selected_ids = request.POST.getlist('selected_contacts')
        if selected_ids:
            try:
                UserContactList.objects.filter(id__in=selected_ids).delete()
                messages.success(request, 'Selected contacts deleted successfully.')
            except Exception as e:
                messages.error(request, f"Error deleting contacts: {e}")
        return redirect('plpapp:list_user_contacts')

    # Get all user contacts
    contacts = UserContactList.objects.filter(user=request.user)

    return render(request, 'plpapp/contact/list_user_contacts.html', {'contacts': contacts})


# poltaker Code ------------------------------------------------------------------------------------------------
from .models import Poltaker

@login_required
def upload_poltakers(request):
    if request.method == 'POST':
        # CSV Upload
        if request.FILES.get('file'):
            upload_file = request.FILES['file']
            fs = FileSystemStorage()
            filename = fs.save(upload_file.name, upload_file)
            file_path = fs.path(filename)

            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(file_path)
                else:
                    df = pd.read_excel(file_path)

                created = 0
                failed = []

                for index, row in df.iterrows():
                    try:
                        email = str(row.get('email')).strip()
                        if not email:
                            continue
                        Poltaker.objects.update_or_create(
                            email=email,
                            defaults={
                                'user': request.user,
                                'name': str(row.get('name')).strip(),
                                'mobile': str(row.get('mobile')).strip(),
                                'zip_code': str(row.get('zip_code')).strip(),
                                'Street': str(row.get('Street')).strip(),
                                'city': str(row.get('city')).strip(),
                                'state': str(row.get('state')).strip(),
                                'password': str(row.get('password')).strip(),
                            }
                        )
                        created += 1
                    except Exception as e:
                        failed.append(f"Row {index+2}: {e}")

                if created:
                    messages.success(request, f"{created} poltakers uploaded successfully.")
                if failed:
                    messages.warning(request, f"Some rows failed:\n" + "\n".join(failed))
            except Exception as e:
                messages.error(request, f"Error processing file: {e}")

            return redirect('plpapp:upload_poltakers')

        # Manual Entry
        elif request.POST.get('manual_name'):
            try:
                Poltaker.objects.create(
                    user=request.user,
                    name=request.POST.get('manual_name'),
                    mobile=request.POST.get('manual_mobile', '0'),
                    email=request.POST.get('manual_email'),
                    zip_code=request.POST.get('manual_zip', '0'),
                    Street=request.POST.get('manual_street', '0'),
                    city=request.POST.get('manual_city', '0'),
                    state=request.POST.get('manual_state', '0'),
                    password=request.POST.get('manual_password', '0'),
                )
                messages.success(request, "Poltaker added successfully.")
            except Exception as e:
                messages.error(request, f"Error adding manually: {e}")
            return redirect('plpapp:upload_poltakers')

    return render(request, 'plpapp/poltaker/upload_poltakers.html')


@login_required
def list_poltakers(request):
    poltakers = Poltaker.objects.filter(user=request.user)

    if request.method == 'POST':
        # Bulk delete selected poltakers
        if 'delete_selected' in request.POST:
            selected_ids = request.POST.getlist('selected_ids')
            if selected_ids:
                Poltaker.objects.filter(id__in=selected_ids).delete()
                messages.success(request, "Selected poltakers deleted successfully.")
            else:
                messages.warning(request, "No poltakers selected to delete.")
        return redirect('plpapp:list_poltakers')

    return render(request, 'plpapp/poltaker/list_poltakers.html', {'poltakers': poltakers})





# USer Profile things update reset ----------------------------------------------------------------------------------------------
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash, authenticate, login
from django.contrib.auth.models import User
from .models import UserProfile

@login_required
def view_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    return render(request, 'plpapp/profile/view_profile.html', {'user_profile': user_profile})

@login_required
def edit_profile(request):
    user_profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update the user profile details
        user_profile.first_name = request.POST.get('first_name', user_profile.first_name)
        user_profile.last_name = request.POST.get('last_name', user_profile.last_name)
        user_profile.phone = request.POST.get('phone', user_profile.phone)
        user_profile.street = request.POST.get('street', user_profile.street)
        user_profile.city = request.POST.get('city', user_profile.city)
        user_profile.state = request.POST.get('state', user_profile.state)
        user_profile.zipcode = request.POST.get('zipcode', user_profile.zipcode)

        # Check if there's a profile picture to upload
        if request.FILES.get('profile_picture'):
            user_profile.profile_picture = request.FILES['profile_picture']

        user_profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('plpapp:view_profile')
    
    return render(request, 'plpapp/profile/edit_profile.html', {'user_profile': user_profile})

@login_required
def change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')

        if new_email and new_email != request.user.email:
            # Update the email of the user
            request.user.email = new_email
            request.user.save()
            messages.success(request, 'Email updated successfully.')
            return redirect('plpapp:view_profile')
        else:
            messages.error(request, 'The new email is the same as the current email or invalid.')

    return render(request, 'plpapp/profile/change_email.html')

@login_required
def reset_password(request):
    if request.method == 'POST':
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if new_password == confirm_new_password:
            # Update the password
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)  # Keep the user logged in after password change
            messages.success(request, 'Password reset successfully.')
            return redirect('plpapp:view_profile')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'plpapp/profile/reset_password.html')

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash

@login_required
def reset_password(request):
    if request.method == 'POST':
        # Get the new password and confirmation from the POST data
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if new_password == confirm_new_password:
            # Update the user's password
            request.user.set_password(new_password)
            request.user.save()

            # Keep the user logged in after password change
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Password reset successfully.')
            return redirect('plpapp:view_profile')
        else:
            messages.error(request, 'Passwords do not match.')

    return render(request, 'plpapp/profile/reset_password.html')



# Analytics View -------------------------------------------------------------------
from surveyapp.models import Survey
from mainapp.models import UserSubscription



@login_required
def analytics_view(request):
    # Filter by date range if provided
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    surveys = Survey.objects.filter(created_by=request.user)
    
    if start_date and end_date:
        surveys = surveys.filter(survey_date__range=[start_date, end_date])
    
    # Calculate all the statistics
    total_surveys = surveys.count()
    completed_surveys = surveys.filter(status='completed').count()
    pending_surveys = surveys.filter(status='pending').count()
    denied_surveys = surveys.filter(status='in_progress').count()
    
    # Survey completion rate
    completion_rate = (completed_surveys / total_surveys) * 100 if total_surveys > 0 else 0
    
    # User's subscription details
    subscription = UserSubscription.objects.filter(user=request.user).first()
    
    context = {
        'subscription': subscription,
        'surveys': surveys,
        'total_surveys': total_surveys,
        'completed_count': completed_surveys,
        'pending_count': pending_surveys,
        'denied_count': denied_surveys,
        'completion_rate': round(completion_rate, 2),
        'completion_percentage': round(completion_rate, 2),  # Alternative name for template
        'start_date': start_date,
        'end_date': end_date
    }
    return render(request, 'analytics.html', context)


from django.shortcuts import render
from .models import AppNotifications
def notifications_view(request):
    notifications = AppNotifications.objects.all().order_by('-created_at')  # Latest first
    return render(request, 'mainapp/notifications.html', {'notifications': notifications})

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import HelpRequest

@login_required
def help_center_view(request):
    if request.method == 'POST':
        subject = request.POST.get('subject')
        message_text = request.POST.get('message')

        if subject and message_text:
            HelpRequest.objects.create(
                user=request.user,
                subject=subject,
                message=message_text
            )
            messages.success(request, "Your request has been submitted successfully.")

    return render(request, 'mainapp/help_center.html')


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import UserSettings

@login_required
def user_settings_view(request):
    user = request.user
    settings, created = UserSettings.objects.get_or_create(user=user)

    if request.method == 'POST':
        # Update settings from POST data
        settings.email_notifications = (request.POST.get('email_notifications') == 'on')
        settings.push_notifications = (request.POST.get('push_notifications') == 'on')
        settings.marketing_emails = (request.POST.get('marketing_emails') == 'on')

        settings.profile_visibility = request.POST.get('profile_visibility', 'private')
        settings.data_collection = request.POST.get('data_collection', 'deny')
        settings.two_factor = request.POST.get('two_factor', 'disabled')

        settings.save()
        message = "Settings saved successfully."
    else:
        message = None

    context = {
        'settings': settings,
        'message': message,
    }
    return render(request, 'mainapp/user_settings.html',context)

from django.contrib.auth import authenticate, logout
@login_required
def delete_account_view(request):
    if request.method == 'POST':
        password = request.POST.get('password')

        # Check if password is correct
        user = authenticate(username=request.user.username, password=password)
        if user is not None:
            # Password correct, delete account
            request.user.delete()
            logout(request)
            messages.success(request, "Your account has been deleted successfully.")
            return redirect('home')  # Change 'home' to your homepage url name
        else:
            messages.error(request, "Incorrect password. Please try again.")

    return render(request, 'mainapp/delete_account.html')