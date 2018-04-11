class RootException(Exception):
    """Base class for exceptions in this module."""
    pass


class RootCredentialsException(RootException):
    """Raised when library/wrapper is used without credentials set in the env variables.

    Attributes:
        message -- explanation of why the specific transition is not allowed
    """

    def __init__(self, message="No ROOT_API_KEY set in environment variables"):
        pass

class RootIdentificationException(RootException):
    """Raised when given identification is not syntactically correct
    Attributes:
        message -- explanation of why syntax was wrong
    """
    def __init__(self, message="identification provided was ill-formed"):
        pass
