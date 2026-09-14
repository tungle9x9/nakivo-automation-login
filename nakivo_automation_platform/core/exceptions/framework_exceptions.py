"""
Custom domain and framework exceptions for the test automation platform.
Enables precise failure triage (AuthenticationRejected vs RateLimited vs InfraFailure).
"""


class FrameworkBaseException(Exception):
    """Base exception for all automation platform errors."""
    pass


class AuthenticationRejected(FrameworkBaseException):
    """Raised when authentication is correctly rejected due to invalid credentials or format."""
    pass


class RateLimitEnforcedException(FrameworkBaseException):
    """
    Raised when server blocks client IP due to brute-force protection (e.g. 5 failed attempts).
    Classified as an Environment/Security State rather than a functional test pass/fail.
    """
    pass


class InfrastructureFailureException(FrameworkBaseException):
    """Raised when target server, network, or Selenium Grid is unreachable or degraded."""
    pass


class ElementInteractionException(FrameworkBaseException):
    """Raised when UI element interaction fails after retries and explicit waits."""
    pass


class ConfigurationException(FrameworkBaseException):
    """Raised when configuration files or environment parameters are invalid."""
    pass
