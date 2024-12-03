from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .forms import UserLoginForm

def user_login(request):
    if request.method == "POST":
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")

            # Authenticate the user using the username field
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/chat/")  # Redirect to the chat page
            else:
                messages.error(request, "Invalid username or password.")

    else:
        form = UserLoginForm()

    return render(request, "login/login.html", {"form": form})
