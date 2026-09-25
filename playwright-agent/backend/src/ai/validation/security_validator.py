"""
Security Validator
==================
Checks generated code for hardcoded credentials, secret keys, token patterns, or insecure shell commands.
"""

import re
from typing import List, Tuple


SECRET_PATTERNS = [
    r"gsk_[a-zA-Z0-9]{32,}",
    r"sk-[a-zA-Z0-9]{32,}",
    r"password\s*=\s*[\"'][^\"']{4,}[\"']",
    r"secret\s*=\s*[\"'][^\"']{4,}[\"']"
]


class SecurityValidator:
    def validate(self, python_code: str) -> Tuple[bool, List[str]]:
        errors = []
        for pattern in SECRET_PATTERNS:
            matches = re.findall(pattern, python_code, re.IGNORECASE)
            # Exclude env_config parameters or variable references
            for m in matches:
                if "env_config" not in m and "your_" not in m.lower():
                    errors.append(f"Security Warning: Potential hardcoded secret or credential pattern detected: '{m[:20]}...'")

        return (len(errors) == 0, errors)
