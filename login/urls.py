from django.urls import path
from .views import CustomLoginView, LogoutView
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Login and Logout URLs
    path("", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),

    # Custom Password Reset URLs
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name="password_reset/password_reset.html"), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(template_name="password_reset/password_reset_done.html"), name="password_reset_done"),
    path("password_reset/confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name="password_reset/password_reset_confirm.html"), name="password_reset_confirm"),
    path("password_reset/complete/", auth_views.PasswordResetCompleteView.as_view(template_name="password_reset/password_reset_complete.html"), name="password_reset_complete"),
]
