from django.urls import path
from .views import register
from . import views


urlpatterns = [
    path("", register, name="register"),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
]