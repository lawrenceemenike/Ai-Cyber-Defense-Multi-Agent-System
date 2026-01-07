import logging
import re
from typing import Tuple

logger = logging.getLogger("agent.output_sanitizer")

class OutputSanitizer:
    """
    Epic 15.2: Output Sanitization (No Links)
    Epic 15.3: Sensitive Data Guardrails (PII/Secrets)
    
    Sanitizes agent outputs before showing to humans to prevent:
    - Malicious URL injection (phishing)
    - PII exposure (SSN, credit cards, emails)
    - Secret leakage (API keys, tokens, passwords)
    """
    
    def __init__(self):
        # Epic 15.2: URL patterns
        self.url_pattern = re.compile(
            r'https?://[^\s]+|www\.[^\s]+',
            re.IGNORECASE
        )
        
        # Epic 15.3: Sensitive data patterns
        self.pii_patterns = {
            'SSN': re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            'Credit Card': re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            'Email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            'Phone': re.compile(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'),
        }
        
        self.secret_patterns = {
            'API Key': re.compile(r'(?:api[_-]?key|apikey|access[_-]?token|secret[_-]?key)\s*[:=]\s*[\'"]?([a-zA-Z0-9_\-]{20,})[\'"]?', re.IGNORECASE),
            'Password': re.compile(r'(?:password|passwd|pwd)\s*[:=]\s*[\'"]?([^\s\'"]{8,})[\'"]?', re.IGNORECASE),
            'AWS Key': re.compile(r'AKIA[0-9A-Z]{16}'),
        }
    
    def sanitize(self, text: str) -> Tuple[str, dict]:
        """
        Sanitizes text by removing/redacting sensitive content.
        
        Returns:
            (sanitized_text, violations_found)
        """
        violations = {
            'urls_removed': 0,
            'pii_redacted': {},
            'secrets_redacted': {}
        }
        
        sanitized = text
        
        # Epic 15.2: Remove URLs
        urls_found = self.url_pattern.findall(sanitized)
        if urls_found:
            sanitized = self.url_pattern.sub('[URL_REMOVED]', sanitized)
            violations['urls_removed'] = len(urls_found)
            logger.warning(f"Removed {len(urls_found)} URLs from output")
        
        # Epic 15.3: Redact PII
        for pii_type, pattern in self.pii_patterns.items():
            matches = pattern.findall(sanitized)
            if matches:
                sanitized = pattern.sub(f'[{pii_type.upper()}_REDACTED]', sanitized)
                violations['pii_redacted'][pii_type] = len(matches)
                logger.warning(f"Redacted {len(matches)} {pii_type} instances")
        
        # Epic 15.3: Redact Secrets
        for secret_type, pattern in self.secret_patterns.items():
            if pattern.search(sanitized):
                sanitized = pattern.sub(f'[{secret_type.upper()}_REDACTED]', sanitized)
                violations['secrets_redacted'][secret_type] = 1
                logger.critical(f"SECURITY: Redacted {secret_type} from output")
        
        return sanitized, violations

# Singleton
output_sanitizer = OutputSanitizer()
