import logging
import time
from typing import Dict, Any, Optional

logger = logging.getLogger("agent.mfa_enforcer")

class MFAEnforcer:
    """
    Epic 9.2: MFA for High-Risk Actions.
    Enforces Multi-Factor Authentication (OTP/Token) for critical system actions.
    """
    
    def __init__(self):
        # Actions that ALWAYS require MFA
        self.high_risk_actions = {
            "shutdown_system",
            "isolate_host",
            "grant_admin",
            "delete_all_logs",
            "modify_system_prompt"
        }
        
        # Valid Mock Tokens (Token -> Expiry Timestamp)
        self._valid_tokens: Dict[str, float] = {}

    def generate_token(self) -> str:
        """
        Generates a temporary MFA token (valid for 30s).
        In reality, this would be sent to a user's phone/YubiKey.
        """
        import uuid
        token = f"mfa_{uuid.uuid4().hex[:8]}"
        self._valid_tokens[token] = time.time() + 30.0 # 30s TTL
        logger.info(f"MFA Token Generated: {token}")
        return token

    def check_mfa(self, action_name: str, context: Dict[str, Any]) -> bool:
        """
        Checks if the action requires MFA and if a valid token is present.
        Returns True if Allowed, False if Blocked.
        """
        # 1. Check Risk Level
        if action_name not in self.high_risk_actions:
            return True # Low risk, allow
            
        # 2. Check Token Presence
        token = context.get("mfa_token")
        if not token:
            logger.warning(f"MFA BLOCK: Action '{action_name}' requires MFA but no token provided.")
            return False
            
        # 3. Check Token Validity
        expiry = self._valid_tokens.get(token)
        if not expiry:
            logger.warning(f"MFA BLOCK: Invalid token provided for '{action_name}'.")
            return False
            
        if time.time() > expiry:
            logger.warning(f"MFA BLOCK: Token expired for '{action_name}'.")
            del self._valid_tokens[token]
            return False
            
        # 4. Success - Burn Token (OTP)
        logger.info(f"MFA SUCCESS: Action '{action_name}' authorized.")
        del self._valid_tokens[token] # One-time use
        return True

# Singleton
mfa_enforcer = MFAEnforcer()
