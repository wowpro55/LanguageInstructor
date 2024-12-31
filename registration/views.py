from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib import messages
from .forms import UserRegistrationForm
from .utils import send_verification_email
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            
            user.set_password(form.cleaned_data["password"])
            
            # Make the user inactive until they verify their email
            user.is_active = False  

            # Send the verification email
            send_verification_email(user, request)

            # Inform the user that a verification email has been sent
            messages.success(request, "A verification email has been sent. Please check your inbox to activate your account.")

            return redirect('/login/') 
    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})

def verify_email(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your email has been successfully verified!")
        return redirect('/login/')
    else:
        messages.error(request, "The verification link is invalid or expired.")
        return redirect('/login/')
