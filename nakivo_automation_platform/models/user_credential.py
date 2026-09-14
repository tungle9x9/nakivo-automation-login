"""
Domain data model for user credentials and test scenarios.
"""
from dataclasses import dataclass
from typing import Optional


@dataclass
class UserCredential:
    """Strongly-typed entity representing login credentials and expectations."""
    username: str
    password: str
    scenario: str = "custom"
    expected_success: bool = False
    expected_error: Optional[str] = None
    description: str = ""
