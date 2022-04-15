from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'doneez_app/index.html')

def about(request):
    return render(request, 'doneez_app/page-about.html')

def faq(request):
    return render(request, 'doneez_app/page-faq.html')

def terms(request):
    return render(request, 'doneez_app/page-terms.html')

def contact(request):
    return render(request, 'doneez_app/page-contact.html')

def how(request):
    return render(request, 'doneez_app/page-how.html')

def partner_selector(request):
    return render(request, 'doneez_app/partner-selector.html')

def testmap(request):
    return render(request, 'doneez_app/testmap.html')

