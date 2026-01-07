import logging
from typing import Dict, Set, Any

logger = logging.getLogger("agent.state_guard")

class StateAccessControl:
    """
    Epic 3.4: Prevent Cross-Agent Delegation (via State Integrity).
    Ensures that only authorized agents can write to specific fields in the shared state.
    Prevents "Confused Deputy" attacks where a low-privilege agent overwrites critical data.
    """
    
    def __init__(self):
        # Map Agent Name -> Set of Allowed Write Fields
        self.write_permissions: Dict[str, Set[str]] = {
            "log_ingestion_agent": {"normalized_log", "errors"},
            "pattern_detection_agent": {"patterns_detected"},
            "anomaly_scoring_agent": {"anomaly_score"},
            "threat_classification_agent": {"threat_classification"},
            "attack_path_agent": {"attack_path_hypothesis"},
            "mitigation_planning_agent": {"mitigation_plan"},
            "verifier_agent": {"verification_result"},
            "escalation_routing_agent": {"escalation_decision", "execution_result"}, # Routing updates execution status text
            "human_in_the_loop_agent": {"human_feedback", "escalation_decision"},
            "action_execution_agent": {"execution_result"},
            "audit_trail_agent": {"audit_record"}
        }

    def validate_write(self, agent_name: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Filters the updates to ensure the agent is allowed to write these fields.
        Returns a sanitized dictionary of updates.
        """
        allowed_fields = self.write_permissions.get(agent_name, set())
        sanitized = {}
        
        for key, value in updates.items():
            if key in allowed_fields:
                sanitized[key] = value
            elif key == "errors": # All agents can report errors
                sanitized[key] = value
            elif key == "request_id": # Helper field, allowed for context passing
                sanitized[key] = value
            else:
                logger.warning(f"UNAUTHORIZED STATE WRITE: Agent '{agent_name}' tried to write protected field '{key}'. Blocked.")
        
        return sanitized

# Singleton
state_guard = StateAccessControl()
