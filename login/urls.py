from django.urls import path
from .views import CustomLoginView, LogoutView

urlpatterns = [
    path("", CustomLoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name='logout')
]
