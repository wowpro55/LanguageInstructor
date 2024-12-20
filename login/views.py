from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.views import View
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from .forms import UserLoginForm



class CustomLoginView(LoginView):
    template_name = "login/login.html"
    redirect_authenticated_user = True
    authentication_form = UserLoginForm
    success_url = reverse_lazy("chat")

    def form_invalid(self, form):
        messages.error(self.request, "Invalid username or password. Please try again.")
        return super().form_invalid(form)

class LogoutView(View):
    def get(self, request):
        """Logs out the user and redirects them to the landing page."""
        logout(request)
        return redirect('landing_page')


def send_password_reset_email(request, user):
    subject = 'Reset Your Password'
    
    # Generate UID and token for the password reset link
    uid = urlsafe_base64_encode(user.pk.encode())
    token = default_token_generator.make_token(user)

    # Context for the email
    context = {
        'user': user,
        'uid': uid,
        'token': token,
        'protocol': request.scheme,
        'domain': get_current_site(request).domain,
    }

    # Render the email message from the template
    message = render_to_string('templates/password_reset/password_reset_email.html', context)

    # Send the email
    send_mail(
        subject,
        message,
        'no-reply@yourdomain.com',
        [user.email],
        html_message=message,
    )
