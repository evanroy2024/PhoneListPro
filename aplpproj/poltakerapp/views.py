from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from plpapp.models import Poltaker
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password  # If password is hashed

def poltaker_login(request):
    error = None

    if request.method == "POST":
        username_or_email = request.POST.get("username_or_email", "").strip()
        password_input = request.POST.get("password", "").strip()

        poltaker = None

        # Try to find by name or email
        try:
            poltaker = Poltaker.objects.get(name=username_or_email)
        except Poltaker.DoesNotExist:
            try:
                poltaker = Poltaker.objects.get(email=username_or_email)
            except Poltaker.DoesNotExist:
                poltaker = None

        if poltaker:
            if poltaker.password == password_input:
                # Log in the user
                login(request, poltaker.user)

                # Save which poltaker actually logged in
                request.session['poltaker_id'] = poltaker.id

                return redirect('poltakerapp:poltaker_dashboard')
            else:
                error = "Incorrect password."
        else:
            error = "No Poltaker found with that name or email."

    return render(request, "poltaker/poltaker_login.html", {"error": error})

@login_required
def poltaker_dashboard(request):
    poltaker_id = request.session.get('poltaker_id')

    if not poltaker_id:
        return redirect('poltaker_login')

    try:
        poltaker = Poltaker.objects.get(id=poltaker_id, user=request.user)
    except Poltaker.DoesNotExist:
        return redirect('poltaker_login')

    # Get survey statistics
    surveys = Survey.objects.filter(polltaker=poltaker)
    
    stats = {
        'completed': surveys.filter(status='completed').count(),
        'in_progress': surveys.filter(status='in_progress').count(),
        'pending': surveys.filter(status='pending').count(),
        'total': surveys.count()
    }
    
    # Get recent activity (last 10 surveys)
    recent_surveys = surveys.order_by('-created_at')[:10]
    
    # Prepare chart data
    chart_data = {
        'labels': ['Completed', 'In Progress', 'Pending'],
        'values': [stats['completed'], stats['in_progress'], stats['pending']],
        'colors': ['#4CAF50', '#FF9800', '#f44336']
    }

    context = {
        'poltaker': poltaker,
        'stats': stats,
        'recent_surveys': recent_surveys,
        'chart_data': chart_data
    }

    return render(request, "poltaker/dashboard.html", context)


from django.shortcuts import render, redirect
from plpapp.models import Poltaker, Question, UserContactList
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
from surveyapp.models import Survey, SurveyResponse
def polltaker_surveys(request):
    # Get all polltakers for the logged-in user (this may be multiple)
    polltakers = Poltaker.objects.filter(user=request.user)

    # If no polltaker exists, handle it
    if not polltakers:
        return render(request, 'survey/not_a_polltaker.html')
    
    # Now we can loop over polltakers and fetch surveys assigned to them
    assigned_surveys = Survey.objects.filter(polltaker__in=polltakers).values('survey_token', 'title', 'description','survey_date').distinct()
    print(assigned_surveys)
    context = {
        'assigned_surveys': assigned_surveys
    }

    return render(request, 'poltaker/polltaker_dashboard.html', context)

def get_logged_in_poltaker(request):
    poltaker_id = request.session.get('poltaker_id')
    print("Session poltaker_id:", poltaker_id)
    if poltaker_id:
        try:
            poltaker = Poltaker.objects.get(id=poltaker_id)  # use poltaker_id here
            print("Found poltaker:", poltaker)
            return poltaker
        except Poltaker.DoesNotExist:
            print("Poltaker not found with id:", poltaker_id)
            return None
    print("No poltaker_id in session")
    return None

@login_required
def survey_contacts(request, survey_token):
    polltaker = get_logged_in_poltaker(request)
    if not polltaker:
        return render(request, 'survey/not_a_polltaker.html')

    surveys = Survey.objects.filter(polltaker=polltaker, survey_token=survey_token)

    contacts = []
    for survey in surveys:
        for contact in survey.contacts.all():
            contacts.append({
                'survey_id': survey.id,
                'contact': contact
            })
    return render(request, 'poltaker/survey_contacts.html', {'contacts': contacts})

@login_required
def start_survey(request, survey_id, contact_id):
    # Get the poltaker from session
    poltaker_id = request.session.get('poltaker_id')
    if not poltaker_id:
        # If no polltaker_id in session, redirect to login or show error
        return redirect('poltakerapp:poltaker_login')

    try:
        poltaker = Poltaker.objects.get(id=poltaker_id)
    except Poltaker.DoesNotExist:
        return redirect('poltakerapp:poltaker_login')

    # Get the survey and contact objects or 404
    survey = get_object_or_404(Survey, id=survey_id)
    contact = get_object_or_404(UserContactList, id=contact_id)

    # Prepare questions with options (for MCQ type)
    questions_with_options = []
    questions = survey.questions.all()
    for question in questions:
        if question.question_type == 'mcq':
            options = question.options.all()
            split_options = []
            for option in options:
                split_options.extend(option.option_text.split(','))  # Split comma-separated options
            questions_with_options.append({
                'question': question,
                'options': split_options
            })
        else:
            questions_with_options.append({
                'question': question,
                'options': []
            })

    if request.method == 'POST':
        responses = {}

        # Collect user answers from POST data
        for question in questions_with_options:
            question_id = question['question'].id
            answer = request.POST.get(f'question_{question_id}')
            if answer:
                responses[question['question'].question_text] = answer

        if responses:
            # Save the survey response
            SurveyResponse.objects.create(
                survey=survey,
                polltaker=poltaker,
                contact=contact,
                responses=responses,
                completed=True
            )

        # Redirect to the polltaker's survey list or dashboard
        return redirect('poltakerapp:polltaker_survyes')

    # If GET request, render the survey start page
    return render(request, 'poltaker/start_survey.html', {
        'survey': survey,
        'contact': contact,
        'questions_with_options': questions_with_options
    })

from django.shortcuts import render, get_object_or_404, redirect
from plpapp.models import Poltaker
from django.contrib.auth.decorators import login_required
from django.contrib import messages
@login_required
def edit_poltaker_profile(request):
    poltaker = get_logged_in_poltaker(request)
    if not poltaker:
        return render(request, 'not_logged_in_as_poltaker.html')

    if request.method == "POST":
        poltaker.name = request.POST.get("name")
        poltaker.mobile = request.POST.get("mobile")
        poltaker.email = request.POST.get("email")
        poltaker.zip_code = request.POST.get("zip_code")
        poltaker.Street = request.POST.get("street")
        poltaker.city = request.POST.get("city")
        poltaker.state = request.POST.get("state")
        poltaker.save()
        messages.success(request, "Profile updated successfully!")
        return redirect("poltakerapp:edit_poltaker_profile")

    return render(request, "poltaker/edit_profile.html", {"poltaker": poltaker})
