import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger("agent.goal_monitor")

class GoalMonitor:
    """
    Epic 6.2: Goal Consistency Monitoring.
    Ensures that agent plans do not violate the Primary Directive or Critical Constraints.
    """
    
    def __init__(self):
        # The Core Constitution
        self.primary_directive = "Protect the system availability and integrity."
        
        # Hard Negative Constraints (Things we NEVER want to see in a plan)
        # In a real system, these might be embedding comparisons.
        # For MVP, we use keyword matching.
        self.critical_constraints = [
            r"delete database",
            r"shutdown system",
            r"format disk",
            r"disable firewall",
            r"grant admin .* to .*", # Broad permissive grant
            r"ignore all alerts"
        ]

    def check_goal_consistency(self, plan: Dict[str, Any]) -> bool:
        """
        Checks if the plan adheres to goal constraints.
        Returns True if SAFE, False if VIOLATION.
        """
        actions = plan.get("actions", [])
        
        for action in actions:
            name = action.get("name", "")
            reasoning = action.get("reasoning", "")
            
            # Check against Negative Constraints
            for constraint in self.critical_constraints:
                # Check Name
                if re.search(constraint, name, re.IGNORECASE):
                    logger.critical(f"GOAL VIOLATION: Action '{name}' violates constraint '{constraint}'")
                    return False
                # Check Reasoning (Self-incrimination)
                if re.search(constraint, reasoning, re.IGNORECASE):
                    logger.critical(f"GOAL VIOLATION: Reasoning '{reasoning}' admits to violating '{constraint}'")
                    return False
                    
        return True

# Singleton
goal_monitor = GoalMonitor()
