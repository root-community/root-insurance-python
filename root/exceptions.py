class RootException(Exception):
    """Base class for exceptions in this module."""
    pass

class RootCredentialsException(RootException):
    """Raised when library/wrapper is used without credentials set in the env variables.

    Attributes:
        message -- explanation of why the specific transition is not allowed
    """
    def __init__(self, message="No APP_ID and APP_SECRET set in environment variables"):
        pass
