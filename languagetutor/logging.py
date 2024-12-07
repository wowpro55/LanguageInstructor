import logging

class SpecialFilter(logging.Filter):
    def __init__(self, foo=None, *args, **kwargs):
        # Now we can handle 'foo' in the filter
        self.foo = foo
        super().__init__(*args, **kwargs)

    def filter(self, record):
        # Custom filtering logic, e.g., checking for specific conditions
        return True


class DBLogHandler(logging.Handler):
    def emit(self, record):
        try:
            from core.utils import log_error
            # Get the error message
            error_message = self.format(record)
            # Log the error into the database using the utility function
            log_error(None, error_message, f"{record.pathname}:{record.lineno}")
        except Exception as e:
            print(f"Error logging to database: {e}")
