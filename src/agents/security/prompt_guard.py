import hashlib
import logging
from typing import Dict

logger = logging.getLogger("agent.prompt_guard")

class PromptGuard:
    """
    Epic 6.1: Immutable Signed System Prompts.
    Ensures that the core system instructions ("Constitution") matches the approved version.
    Prevents authorized users or attackers from subtly altering agent behavior via prompt injection
    at the configuration layer.
    """
    
    def __init__(self):
        # Database of approved system prompts and their SHA-256 hashes
        # In prod, this would be loaded from a read-only secure vault.
        self.approved_prompts: Dict[str, str] = {
            "core_detection": self._hash("You are a detection agent. Identify threats..."),
            "mitigation_planner": self._hash("You are a mitigation planner. Prioritize availability...")
        }

    def _hash(self, text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def register_prompt(self, agent_name: str, prompt_text: str):
        """
        Registers a prompt as 'Golden' (Approved). 
        In a real scenario, this step requires Multi-Party Approval.
        """
        prompt_hash = self._hash(prompt_text)
        self.approved_prompts[agent_name] = prompt_hash
        logger.info(f"Registered Golden Prompt for '{agent_name}'. Hash: {prompt_hash[:8]}...")

    def verify_agent_prompt(self, agent_name: str, current_prompt_text: str) -> bool:
        """
        Verifies that the agent's current prompt matches the Golden Record.
        """
        if agent_name not in self.approved_prompts:
            logger.warning(f"Prompt Verification Failed: Unknown agent '{agent_name}'")
            return False
            
        current_hash = self._hash(current_prompt_text)
        expected_hash = self.approved_prompts[agent_name]
        
        if current_hash != expected_hash:
            logger.critical(f"INTEGRITY VIOLATION: Prompt for '{agent_name}' has been tampered with!")
            logger.critical(f"Expected: {expected_hash}, Got: {current_hash}")
            return False
            
        return True

# Singleton
prompt_guard = PromptGuard()
