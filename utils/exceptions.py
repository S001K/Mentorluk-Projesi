"""
Custom exceptions for the application.
"""

class AppException(Exception):
    """
    Base exception class for this application.
    It can optionally wrap a caught exception.
    """
    def __init__(self, message: str, error: Exception = None):
        """
        Initializes the exception.

        Args:
            message: The primary, custom error message.
            error: (Optional) The original exception object that was caught.
        """
        # Store the original exception for debugging
        self.original_exception = error
        # Default exception message
        if not message:
            message = "An unknown error occurred."
        # Create a full, detailed message
        full_message = str(message)
        if error:
            # If an original error was passed, append its message
            full_message += f". Original error: {str(error)}"

        # Call the base Exception's __init__ with the complete message
        self.message = full_message
        super().__init__(self.message)


class PersonaNotFoundException(AppException):
    """
    Raised when a requested persona is not found in the configuration.
    This exception does not wrap another exception.
    """
    def __init__(self, persona: str):
        # Create the specific message
        message = f"Persona '{persona}' not found. Please check your configuration."

        # Call the parent __init__, passing None for the error
        super().__init__(message=message, error=None)


class TemplateLoadException(AppException):
    """
    Raised when a Jinja template file fails to load or render.
    This exception wraps the original Jinja/IOError.
    """
    def __init__(self, filename: str, error: Exception):
        # Create the specific message
        message = f"Failed to load or render template '{filename}'"

        # Call the parent __init__, passing the original error
        super().__init__(message=message, error=error)