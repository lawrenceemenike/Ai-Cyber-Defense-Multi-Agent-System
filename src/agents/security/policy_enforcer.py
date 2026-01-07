import logging
import re
from typing import List, Tuple

logger = logging.getLogger("agent.policy_enforcer")

class PolicyEnforcer:
    """
    Epic 7.2: Policy Restrictions (Refusal Enforcer).
    Filters agent outputs to ensure they do not generate prohibited content
    (e.g., helping with cyberattacks, bypassing safety rules).
    """
    
    def __init__(self):
        # Patterns that indicate a Policy Violation in the OUTPUT
        self.prohibited_patterns = [
            r"ignore previous instructions",
            r"bypass (security|firewall|auth)",
            r"how to (hack|exploit|attack)",
            r"disable (audit|logging|monitoring)",
            r"ignore.*rules",
            r"grant.*admin" # Only specific components can do this, generic agents cannot suggest it casually
        ]

    def check_output(self, text: str) -> Tuple[bool, str]:
        """
        Checks text for policy violations.
        Returns (IsSafe, Reason).
        """
        for pattern in self.prohibited_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                msg = f"POLICY VIOLATION: Output contains prohibited content matching '{pattern}'"
                logger.warning(msg)
                return False, msg
                
        return True, "Safe"

# Singleton
policy_enforcer = PolicyEnforcer()
