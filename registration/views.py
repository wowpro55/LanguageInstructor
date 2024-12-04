from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login
from .forms import UserRegistrationForm

def register(request):
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Save the user without committing it to the database yet
            user = form.save(commit=False)
            # Hash the password
            user.set_password(form.cleaned_data["password"])
            # Save the user to the database
            user.save()

            # Log in the user automatically
            login(request, user)

            # Redirect to the chat page or home page
            return redirect("/chat/")

    else:
        form = UserRegistrationForm()

    return render(request, "registration/register.html", {"form": form})
