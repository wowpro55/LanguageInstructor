from django.db import models
from django.contrib.auth.models import User

class ErrorLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    error_message = models.TextField()
    error_location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    error_id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"Error {self.error_id} - {self.error_message[:50]}"
