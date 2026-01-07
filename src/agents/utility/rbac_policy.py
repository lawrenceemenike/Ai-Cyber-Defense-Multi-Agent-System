import logging
from typing import Dict, List, Set

logger = logging.getLogger("agent.rbac")

class RBACPolicy:
    """
    Epic 3: Privilege Compromise Prevention via Granular RBAC.
    """
    
    def __init__(self):
        # 3.1: Role Definitions
        self.roles: Dict[str, Set[str]] = {
            "analyst": {"read_logs", "view_plan"},
            "responder_tier_1": {"read_logs", "block_ip", "disable_user"},
            "responder_tier_2": {"read_logs", "isolate_host", "kill_process", "block_ip", "disable_user"},
            "admin": {"*"} # Full access
        }
        
        # Action -> Required Permission Mapping
        self.permissions: Dict[str, str] = {
            "Block Source IP": "block_ip",
            "Disable User Account": "disable_user",
            "Isolate Host Network": "isolate_host",
            "Kill Suspicious Process": "kill_process",
            "Log and Monitor Only": "read_logs"
        }

    def check_permission(self, role: str, action_name: str) -> bool:
        """
        Validates if the user role has permission to execute the action.
        """
        required_perm = self.permissions.get(action_name)
        
        if not required_perm:
            # Safe default: Deny if unknown
            logger.warning(f"RBAC Deny: Unknown action '{action_name}'")
            return False
            
        allowed_perms = self.roles.get(role, set())
        
        if "*" in allowed_perms:
            return True
            
        if required_perm in allowed_perms:
            return True
            
        logger.warning(f"RBAC Deny: Role '{role}' cannot perform '{action_name}'")
        return False

# Singleton
rbac_policy = RBACPolicy()
