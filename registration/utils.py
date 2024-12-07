# utils.py
from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.conf import settings

def send_verification_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(str(user.pk).encode())
    domain = get_current_site(request).domain
    verification_link = reverse('verify_email', kwargs={'uidb64': uid, 'token': token})
    full_link = f'http://{domain}{verification_link}'
    
    subject = "Email Verification"
    message = f'Hello {user.username},\n\nPlease verify your email address by clicking the link below:\n\n{full_link}'

    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
