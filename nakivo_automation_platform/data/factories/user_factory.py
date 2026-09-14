"""
UserFactory implementing dynamic test data generation, boundary values,
and worker-level isolation for parallel pytest-xdist execution.
Does not couple to global singletons; loads from runtime config or environment.
"""
import os
from nakivo_automation_platform.models.user_credential import UserCredential


class UserFactory:
    """Factory generating strongly-typed UserCredential models."""

    @staticmethod
    def valid_admin(config=None) -> UserCredential:
        username = config.admin_username if config else os.getenv("NAKIVO_USER", "admin")
        password = config.admin_password if config else os.getenv("NAKIVO_PASSWORD", "")
        return UserCredential(
            username=username,
            password=password,
            scenario="valid_admin",
            expected_success=True,
            description="Verified system administrator credentials"
        )

    @staticmethod
    def invalid_user() -> UserCredential:
        return UserCredential(
            username="unregistered_user@corp.internal",
            password="WrongPassword999!",
            scenario="invalid_credentials",
            expected_success=False,
            expected_error="Incorrect credentials.",
            description="Unregistered user account"
        )

    @staticmethod
    def empty_username(config=None) -> UserCredential:
        password = config.admin_password if config else os.getenv("NAKIVO_PASSWORD", "")
        return UserCredential(
            username="",
            password=password,
            scenario="empty_username",
            expected_success=False,
            expected_error="required",
            description="Missing username field"
        )

    @staticmethod
    def empty_password(config=None) -> UserCredential:
        username = config.admin_username if config else os.getenv("NAKIVO_USER", "admin")
        return UserCredential(
            username=username,
            password="",
            scenario="empty_password",
            expected_success=False,
            expected_error="required",
            description="Missing password field"
        )

    @staticmethod
    def both_empty() -> UserCredential:
        return UserCredential(
            username="",
            password="",
            scenario="both_empty",
            expected_success=False,
            expected_error="disabled",
            description="Both credentials omitted"
        )

    @staticmethod
    def malformed_email(config=None) -> UserCredential:
        password = config.admin_password if config else os.getenv("NAKIVO_PASSWORD", "")
        return UserCredential(
            username="testuser.com",
            password=password,
            scenario="malformed_email",
            expected_success=False,
            expected_error="valid email",
            description="Malformed email format lacking @"
        )

    @staticmethod
    def excessive_length_email(config=None) -> UserCredential:
        password = config.admin_password if config else os.getenv("NAKIVO_PASSWORD", "")
        long_email = ("a" * 240) + "@domainboundarytest.com"
        return UserCredential(
            username=long_email,
            password=password,
            scenario="excessive_email",
            expected_success=False,
            expected_error="exceed",
            description="Email address exceeding 255 characters"
        )

    @staticmethod
    def excessive_length_password(config=None) -> UserCredential:
        username = config.admin_username if config else os.getenv("NAKIVO_USER", "admin")
        long_pass = "P@" + ("x" * 100) + "9!"
        return UserCredential(
            username=username,
            password=long_pass,
            scenario="excessive_password",
            expected_success=False,
            expected_error="100",
            description="Password exceeding 100 characters"
        )

    @staticmethod
    def for_worker(worker_id="gw0", config=None) -> UserCredential:
        """Provide isolated user per pytest-xdist worker to prevent concurrent lockout."""
        username = config.admin_username if config else os.getenv("NAKIVO_USER", "admin")
        password = config.admin_password if config else os.getenv("NAKIVO_PASSWORD", "")
        return UserCredential(
            username=username,
            password=password,
            scenario=f"worker_{worker_id}",
            expected_success=True,
            description=f"Isolated session for worker {worker_id}"
        )
