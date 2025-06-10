from django.shortcuts import render, redirect
from .models import Survey, Poltaker, Question, UserContactList
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import get_object_or_404
import random
import string
from django.utils import timezone
from django.contrib import messages

def generate_token(length=10):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

@login_required
def create_survey(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        survey_date = request.POST.get('survey_date')
        question_ids = request.POST.getlist('questions')
        contact_ids = request.POST.getlist('contacts')
        polltaker_ids = request.POST.getlist('polltakers')

        questions = Question.objects.filter(id__in=question_ids)
        contacts = UserContactList.objects.filter(id__in=contact_ids)
        polltakers = Poltaker.objects.filter(id__in=polltaker_ids)

        survey_token = generate_token()

        for poltaker in polltakers:
            for contact in contacts:
                survey = Survey.objects.create(
                    title=title,
                    description=description,
                    created_by=request.user,
                    polltaker=poltaker,
                    survey_date=survey_date or timezone.now(),
                    survey_token=survey_token
                )
                survey.questions.set(questions)
                survey.contacts.set([contact])  # Each Survey has one contact
                survey.save()

        return redirect('surveyapp:all_surveys')  # your success page

    context = {
        'questions': Question.objects.all(),
        'contacts': UserContactList.objects.all(),
        'polltakers': Poltaker.objects.all(),
    }
    return render(request, 'survey/create_survey.html', context)


# @login_required
# def all_surveys_view(request):
#     surveys = Survey.objects.filter(created_by=request.user).order_by('-created_at')
#     return render(request, 'survey/all_surveys.html', {'surveys': surveys})

@login_required
def delete_survey_view(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id, created_by=request.user)
    survey.delete()
    messages.success(request, "Survey deleted successfully.")
    return redirect('surveyapp:all_surveys')


# Survey Response Download 
import csv
from django.http import HttpResponse
from .models import Survey, SurveyResponse
from io import BytesIO
from django.http import FileResponse
from reportlab.pdfgen import canvas
from .models import Survey, SurveyResponse
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import csv
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def download_survey_csv(request, survey_id):
    # Get the original survey
    survey = get_object_or_404(Survey, id=survey_id)

    # Get all related surveys with same token
    related_surveys = Survey.objects.filter(survey_token=survey.survey_token)

    # Get all responses for all surveys with same token
    responses = SurveyResponse.objects.filter(survey__in=related_surveys)

    # Prepare CSV response
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="survey_{survey.survey_token}_responses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Contact Name', 'Email', 'Question', 'Answer'])

    for r in responses:
        contact = r.contact
        full_name = f"{contact.first_name} {contact.last_name}" if contact else "Unknown"
        email = contact.email if contact else "N/A"

        for key, answer in r.responses.items():
            if key.isdigit():
                try:
                    question = Question.objects.get(id=int(key))
                    qtext = question.question_text
                except Question.DoesNotExist:
                    qtext = f"Question ID {key}"
            else:
                qtext = key
            writer.writerow([full_name, email, qtext, answer])

    return response


from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

def download_survey_pdf(request, survey_id):
    survey = get_object_or_404(Survey, id=survey_id)
    related_surveys = Survey.objects.filter(survey_token=survey.survey_token)
    responses = SurveyResponse.objects.filter(survey__in=related_surveys)

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                            rightMargin=40, leftMargin=40,
                            topMargin=60, bottomMargin=50)

    styles = getSampleStyleSheet()

    heading_style = ParagraphStyle(
        'HeadingCenter',
        parent=styles['Heading1'],
        alignment=TA_CENTER,
        textColor=colors.HexColor("#4B89DC"),
        spaceAfter=12,
    )

    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        spaceAfter=6,
        leftIndent=0,
    )
    value_style = ParagraphStyle(
        'ValueStyle',
        parent=styles['Normal'],
        fontSize=12,
        leftIndent=10,
        spaceAfter=12,
    )

    elements = []

    # Title centered with color
    elements.append(Paragraph(survey.title, heading_style))

    # Add a horizontal line below the title
    elements.append(Table(
        [['']],
        colWidths=[480],
        style=[('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor("#4B89DC"))]
    ))
    elements.append(Spacer(1, 18))

    # Description and Date table
    survey_description = related_surveys.first().description if related_surveys.exists() else ''
    survey_date = related_surveys.order_by('survey_date').first().survey_date if related_surveys.exists() else None

    desc_date_data = [
        [Paragraph('<b>Description:</b>', label_style), Paragraph(survey_description if survey_description else "N/A", value_style)],
        [Paragraph('<b>Date:</b>', label_style), Paragraph(survey_date.strftime('%B %d, %Y') if survey_date else "N/A", value_style)]
    ]
    desc_date_table = Table(desc_date_data, colWidths=[100, 380], hAlign='LEFT')
    desc_date_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(desc_date_table)

    # Add a horizontal line below description/date
    elements.append(Table(
        [['']],
        colWidths=[480],
        style=[('LINEBELOW', (0,0), (-1,-1), 1, colors.grey)]
    ))
    elements.append(Spacer(1, 24))

    # Responses section
    for idx, r in enumerate(responses, start=1):
        contact = r.contact
        full_name = f"{contact.first_name} {contact.last_name}" if contact else "Unknown"
        email = contact.email if contact else "N/A"

        contact_info = f"<b>Response #{idx}</b> — Contact: <b>{full_name}</b> | Email: <b>{email}</b>"
        elements.append(Paragraph(contact_info, styles['Heading3']))
        elements.append(Spacer(1, 6))

        table_data = [["Question", "Answer"]]
        for key, answer in r.responses.items():
            if key.isdigit():
                try:
                    question = Question.objects.get(id=int(key))
                    qtext = question.question_text
                except Question.DoesNotExist:
                    qtext = f"Question ID {key}"
            else:
                qtext = key

            table_data.append([qtext, answer])

        table = Table(table_data, colWidths=[260, 260], hAlign='LEFT')
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#DCE6F1")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor("#2F5496")),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#B0B7C6")),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F6FB")]),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('LEFTPADDING', (0, 0), (-1, -1), 6),
            ('RIGHTPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
        ]))

        elements.append(table)
        elements.append(Spacer(1, 24))

    def _header_footer(canvas, doc):
        canvas.saveState()
        page_num_text = f"Page {doc.page}"
        canvas.setFont('Helvetica-Oblique', 9)
        canvas.setFillColor(colors.grey)
        canvas.drawRightString(doc.width + 40, 20, page_num_text)
        canvas.restoreState()

    doc.build(elements, onFirstPage=_header_footer, onLaterPages=_header_footer)

    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="survey_{survey.survey_token}_responses.pdf"'
    response.write(pdf)
    return response

from django.db.models import Max
from django.db.models import Max

@login_required
def all_surveys_view(request):
    # Step 1: Get the latest survey ID for each unique token created by the user
    unique_tokens = (
        Survey.objects
        .filter(created_by=request.user)
        .values('survey_token')
        .annotate(latest_id=Max('id'))
    )

    # Step 2: Extract survey IDs from the annotated queryset
    latest_survey_ids = [item['latest_id'] for item in unique_tokens]

    # Step 3: Fetch only those surveys by ID, ensuring only one per token
    surveys = Survey.objects.filter(id__in=latest_survey_ids).order_by('-created_at')

    return render(request, 'survey/all_surveys.html', {'surveys': surveys})


def survey_response_view(request, survey_id):
    # Get the selected survey
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Get all surveys with the same token
    related_surveys = Survey.objects.filter(survey_token=survey.survey_token)
    
    # Get all responses for all related surveys
    responses = SurveyResponse.objects.filter(survey__in=related_surveys)

    formatted_responses = []

    for response in responses:
        contact = response.contact
        contact_name = f"{contact.first_name} {contact.last_name}" if contact else "Unknown"
        email = contact.email if contact else "N/A"

        answers = []
        for key, answer in response.responses.items():
            if key.isdigit():
                try:
                    question = Question.objects.get(id=int(key))
                    question_text = question.question_text
                except Question.DoesNotExist:
                    question_text = f"Question ID {key}"
            else:
                question_text = key

            answers.append({
                'question': question_text,
                'answer': answer,
            })

        formatted_responses.append({
            'contact_name': contact_name,
            'email': email,
            'answers': answers,
        })

    return render(request, 'survey/survey_responses.html', {
        'survey': survey,  # This is fine, just one of the group
        'responses': formatted_responses,
    })
