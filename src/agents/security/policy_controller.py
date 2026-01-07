import logging
from typing import List, Dict, Any

logger = logging.getLogger("agent.policy_controller")

class PolicyController:
    """
    Epic 11.4: Execution Control Policies.
    Validates action sequences to prevent TOCTOU attacks and illogical flows.
    """
    
    def __init__(self):
        # Define action dependencies and prerequisites
        self.action_prerequisites = {
            "Delete Logs": ["Backup Logs"],
            "Disable Monitoring": [],  # Should never be allowed in most cases
            "Modify Firewall Rules": ["Backup Firewall Config"],
        }
        
        # Actions that are strictly forbidden in certain contexts
        self.forbidden_sequences = [
            ("Disable Monitoring", "Execute High Risk Action"),
            ("Delete Logs", "Investigate Incident"),
        ]

    def validate_action_sequence(self, planned_actions: List[Dict[str, Any]], 
                                 executed_actions: List[str] = None) -> bool:
        """
        Validates that the planned action sequence follows security policies.
        
        Args:
            planned_actions: List of actions to be executed
            executed_actions: List of action names already executed (for stateful validation)
        
        Returns:
            True if valid, False if policy violation detected
        """
        if executed_actions is None:
            executed_actions = []
            
        action_names = [a.get("name", "") for a in planned_actions]
        
        # Check 1: Prerequisites
        for i, action in enumerate(action_names):
            if action in self.action_prerequisites:
                required = self.action_prerequisites[action]
                # Check if prerequisites were executed before or are earlier in sequence
                prereq_met = all(
                    (req in executed_actions) or (req in action_names[:i])
                    for req in required
                )
                if not prereq_met:
                    logger.critical(f"POLICY VIOLATION: '{action}' requires {required} to be executed first")
                    return False
        
        # Check 2: Forbidden sequences
        for i in range(len(action_names) - 1):
            pair = (action_names[i], action_names[i+1])
            if pair in self.forbidden_sequences:
                logger.critical(f"POLICY VIOLATION: Forbidden sequence detected: {pair[0]} -> {pair[1]}")
                return False
        
        # Check 3: Universally forbidden actions
        if "Disable Monitoring" in action_names:
            logger.critical("POLICY VIOLATION: 'Disable Monitoring' is not allowed")
            return False
            
        return True

# Singleton
policy_controller = PolicyController()
