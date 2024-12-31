from django.shortcuts import render

def welcome_page(request):
    return render(request, "welcome_page/index.html")
