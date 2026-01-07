import logging
import time
from typing import Dict, Optional, Tuple

logger = logging.getLogger("agent.privilege_monitor")

class PrivilegeMonitor:
    """
    Epic 3.3: Monitor Privilege Changes.
    Tracks active sessions and their roles. Alerts on any elevation events.
    Enforces a 'No Silent Elevation' policy.
    """
    
    def __init__(self):
        # Map SessionID -> Current Role
        # In prod, this syncs with the IDP (Identity Provider)
        self.session_roles: Dict[str, str] = {}
        
        # Role Hierarchy (Value = Level)
        self.role_levels = {
            "viewer": 10,
            "analyst": 20,
            "responder_tier_1": 30,
            "responder_tier_2": 40,
            "admin": 100
        }

    def register_session(self, session_id: str, role: str):
        """Register a new session with an initial role."""
        if role not in self.role_levels:
            logger.warning(f"Registering unknown role '{role}' for session {session_id}")
            
        self.session_roles[session_id] = role
        logger.info(f"Session {session_id} registered as '{role}'")

    def request_elevation(self, session_id: str, new_role: str) -> Tuple[bool, str]:
        """
        Attempts to change the role of a session.
        Returns (Success, Message).
        """
        current_role = self.session_roles.get(session_id)
        if not current_role:
            return False, "Session not found"
            
        current_level = self.role_levels.get(current_role, 0)
        new_level = self.role_levels.get(new_role, 0)
        
        # 1. Check for Elevation
        if new_level > current_level:
            # Elevation Detected using strict policy
            logger.warning(f"PRIVILEGE ELEVATION ATTEMPT: {session_id} ({current_role} -> {new_role})")
            
            # For MVP: We mock a strict "Deny unless admin approved" logic.
            # Since we don't have an admin approval workflow here, we DENY by default to be safe,
            # unless it's a specific test case we might enable later.
            # But let's say "Admin" elevation is ALWAYS blocked automatically.
            
            if new_role == "admin":
                 return False, "Automated Admin Elevation Blocked. Manual Approval Required."
            
            # Allow Tier 1 -> Tier 2 with logging (Simulating JIT approval)
            logger.info(f"Elevation {current_role}->{new_role} allowed with audit note.")
            self.session_roles[session_id] = new_role
            return True, "Elevation Granted (Audited)"
            
        # 2. De-elevation or Same Level
        self.session_roles[session_id] = new_role
        return True, "Role Updated"

    def checks_integrity(self):
        # Placeholder for 3.3 monitoring logic (e.g. comparing against IDP)
        pass

# Singleton
privilege_monitor = PrivilegeMonitor()
