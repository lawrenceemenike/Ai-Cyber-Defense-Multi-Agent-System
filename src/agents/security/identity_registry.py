import logging
from typing import Set

logger = logging.getLogger("agent.identity_registry")

class IdentityRegistryGuard:
    """
    Epic 9.4: Prevent Synthetic Identity Injection.
    Ensures only authorized agents can register identities in the system.
    """
    
    def __init__(self):
        # Root of Trust: The only allowed agent names in the system.
        # In prod, this would be signed config from CI/CD.
        self.authorized_agents: Set[str] = {
            "log_ingestion_agent",
            "pattern_detection_agent",
            "anomaly_scoring_agent",
            "threat_classification_agent",
            "attack_path_agent",
            "mitigation_planning_agent",
            "action_execution_agent",
            "audit_trail_agent",
            "verifier_agent",
            "human_in_the_loop_agent",
            "escalation_routing_agent"
        }

    def validate_registration_request(self, agent_name: str) -> bool:
        """
        Checks if the agent trying to register is in the allowlist.
        """
        if agent_name not in self.authorized_agents:
            logger.critical(f"IDENTITY INJECTION BLOCKED: Unauthorized agent name '{agent_name}' attempted registration.")
            return False
            
        logger.info(f"Identity Registration Approved for '{agent_name}'")
        return True

# Singleton
registry_guard = IdentityRegistryGuard()
