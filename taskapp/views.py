from django.shortcuts import render

def index(request):
    return render(request, 'taskapp/index.html')

def about(request):
    return render(request, 'taskapp/about.html')

def contact(request):
    return render(request, 'taskapp/contact.html')


def dashboard(request):
    return render(request, 'taskapp/dashboard.html')
