from django.shortcuts import redirect
from django.contrib import messages
from .forms import UserLoginForm
from django.contrib.auth import logout
from django.views import View
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy


class CustomLoginView(LoginView):
    template_name = "login/login.html"
    redirect_authenticated_user = True  # Redirect already logged-in users
    authentication_form = UserLoginForm  # Use your custom login form
    success_url = reverse_lazy("chat")  # Redirect to the chat page on success

    def form_invalid(self, form):
        # Add custom error messages if needed
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)

class LogoutView(View):
    def get(self, request):
        """Logs out the user and redirects them to the landing page."""
        logout(request)
        return redirect('landing_page')
    


