"""
Enterprise logger with automated sensitive data masking (passwords, tokens, credentials).
"""
import re
import logging
import sys

SENSITIVE_PATTERNS = [
    (re.compile(r"(password['\"]?\s*[:=]\s*['\"]?)([^'\",\s]+)(['\"]?)", re.IGNORECASE), r"\1******\3"),
    (re.compile(r"(token['\"]?\s*[:=]\s*['\"]?)([^'\",\s]+)(['\"]?)", re.IGNORECASE), r"\1******\3"),
    (re.compile(r"(secret['\"]?\s*[:=]\s*['\"]?)([^'\",\s]+)(['\"]?)", re.IGNORECASE), r"\1******\3"),
    (re.compile(r"(otp['\"]?\s*[:=]\s*['\"]?)([^'\",\s]+)(['\"]?)", re.IGNORECASE), r"\1******\3"),
]


class MaskingFormatter(logging.Formatter):
    """Logging Formatter that intercepts and masks sensitive strings."""

    def format(self, record):
        original = super().format(record)
        masked = original
        for pattern, replacement in SENSITIVE_PATTERNS:
            masked = pattern.sub(replacement, masked)
        return masked


class MaskedLogger:
    """Factory for masked loggers."""

    @staticmethod
    def get_logger(name="SDET-Platform"):
        logger = logging.getLogger(name)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = logging.StreamHandler(sys.stdout)
            formatter = MaskingFormatter(
                fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger
