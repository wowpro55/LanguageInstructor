from django.urls import path
from .views import register
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path("", register, name="register"),
    path('verify-email/<uidb64>/<token>/', views.verify_email, name='verify_email'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]