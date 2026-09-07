"""
Rule-Based Pre-Embedding Moderation & Masking Layer
===================================================
Enforces deterministic security boundaries before content reaches embedding models
or vector databases. Masks PII/credentials and blocks toxic/inappropriate content.
"""

import json
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple


class ModerationResult:
    def __init__(
        self,
        status: str,
        blocked: bool,
        reason: Optional[str] = None,
        masked_fields: Optional[List[str]] = None,
        sanitized_content: str = "",
        message: str = ""
    ):
        self.status = status  # "ALLOWED" or "BLOCKED"
        self.blocked = blocked
        self.reason = reason
        self.masked_fields = masked_fields or []
        self.sanitized_content = sanitized_content
        self.message = message

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "blocked": self.blocked,
            "reason": self.reason,
            "maskedFields": self.masked_fields,
            "sanitizedContent": self.sanitized_content,
            "message": self.message
        }


class ContentModerator:
    """
    Deterministic rule-based moderation engine.
    Ensures no raw URLs, emails, usernames, passwords, or toxic text are sent to external APIs.
    """

    DEFAULT_TOXIC_TERMS = {
        "drop database",
        "rm -rf",
        "shutdown -h",
        "format c:",
        ":(){ :|:& };:",
        "delete from users",
        "eval(",
        "__import__('os').system",
        "malicious_payload",
        "exploit_kit"
    }

    # URL regex: matches http, https, ftp, or standard hostnames
    URL_REGEX = re.compile(
        r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|https?:\/\/[a-zA-Z0-9\-._~:/?#\[\]@!$&'()*+,;=]+)",
        re.IGNORECASE
    )

    # Email regex
    EMAIL_REGEX = re.compile(
        r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
        re.IGNORECASE
    )

    # Explicit credential field assignments like username = "...", password: "..."
    PASSWORD_ASSIGNMENT_REGEX = re.compile(
        r"""(?i)(?:password|passwd|pwd|secret|api_key|token)\s*[:=]\s*["']([^"']+)["']"""
    )
    USERNAME_ASSIGNMENT_REGEX = re.compile(
        r"""(?i)(?:username|user_name|login_id|logonId)\s*[:=]\s*["']([^"']+)["']"""
    )

    def __init__(
        self,
        toxic_terms: Optional[Set[str]] = None,
        mask_urls: bool = True,
        mask_emails: bool = True,
        mask_credentials: bool = True
    ):
        self.toxic_terms = set(toxic_terms) if toxic_terms else set(self.DEFAULT_TOXIC_TERMS)
        self.mask_urls = mask_urls
        self.mask_emails = mask_emails
        self.mask_credentials = mask_credentials

    def moderate_and_sanitize(self, content: str) -> ModerationResult:
        """
        Runs deterministic checks on raw text.
        1. Checks for toxic/inappropriate terms (blocks if found).
        2. Masks URLs, emails, and credentials.
        Returns a ModerationResult with sanitized text.
        """
        if not content:
            return ModerationResult(status="ALLOWED", blocked=False, sanitized_content="")

        # 1. Toxicity / Inappropriate Check
        lower_content = content.lower()
        for term in self.toxic_terms:
            if term.lower() in lower_content:
                return ModerationResult(
                    status="BLOCKED",
                    blocked=True,
                    reason="TOXIC_CONTENT",
                    message=f"The submitted content contains prohibited term/operation.",
                    sanitized_content=""
                )

        sanitized = content
        masked_fields: List[str] = []

        # 2. Mask Passwords / Secrets
        if self.mask_credentials:
            if self.PASSWORD_ASSIGNMENT_REGEX.search(sanitized):
                sanitized = self.PASSWORD_ASSIGNMENT_REGEX.sub(r'password = "[MASKED_PASSWORD]"', sanitized)
                masked_fields.append("password")

            if self.USERNAME_ASSIGNMENT_REGEX.search(sanitized):
                sanitized = self.USERNAME_ASSIGNMENT_REGEX.sub(r'username = "[MASKED_USERNAME]"', sanitized)
                masked_fields.append("username")

        # 3. Mask Emails
        if self.mask_emails:
            if self.EMAIL_REGEX.search(sanitized):
                sanitized = self.EMAIL_REGEX.sub("[MASKED_EMAIL]", sanitized)
                masked_fields.append("email")

        # 4. Mask URLs
        if self.mask_urls:
            if self.URL_REGEX.search(sanitized):
                sanitized = self.URL_REGEX.sub("[MASKED_URL]", sanitized)
                masked_fields.append("url")

        return ModerationResult(
            status="ALLOWED",
            blocked=False,
            masked_fields=list(set(masked_fields)),
            sanitized_content=sanitized,
            message="Content successfully moderated and sanitized."
        )
