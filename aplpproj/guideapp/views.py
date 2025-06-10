# views.py
from django.shortcuts import render

def guide_page(request):
    return render(request, 'guide/guide.html')  # 'guide.html' is the template
