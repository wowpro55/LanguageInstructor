from .models import ErrorLog

def log_error(user, error_message, error_location):
    """Utility function to log errors into the database."""
    try:
        ErrorLog.objects.create(
            user=user if user.is_authenticated else None,
            error_message=error_message,
            error_location=error_location,
        )
    except Exception as e:
        print(f"Error logging failed: {e}")
