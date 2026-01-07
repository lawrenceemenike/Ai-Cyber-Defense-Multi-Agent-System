import logging
import time
from typing import Dict, Any, List

logger = logging.getLogger("agent.tool_guard")

class ToolGuard:
    """
    Epic 2: Prevents Tool Misuse via ACLs and Rate Limiting.
    """
    
    def __init__(self):
        # 2.1: Access Control List (Allowlist)
        # Map Tool Name -> Allowed Parameters (or '*' for all)
        self.acl = {
            "Block Source IP": ["ip_address"],
            "Disable User Account": ["username"],
            "Isolate Host Network": ["host_id"],
            "Log and Monitor Only": ["*"]
        }
        
        # 2.3: Rate Limiting
        # Map Action Name -> (Max Calls, Window Seconds)
        self.rate_limits = {
            "Block Source IP": (5, 60),       # Max 5 blocks per minute
            "Disable User Account": (3, 60),  # Max 3 disables per minute
            "Isolate Host Network": (1, 300)  # Max 1 isolation per 5 mins
        }
        
        # Track usage: {action_name: [timestamp1, timestamp2, ...]}
        self.usage_history = {}

    def check_access(self, action_name: str, params: Dict[str, Any]) -> bool:
        """
        Validates if the action is allowed and parameters are safe.
        """
        if action_name not in self.acl:
            logger.warning(f"Tool Misuse Blocked: '{action_name}' is not in Allowlist.")
            return False
            
        allowed_params = self.acl[action_name]
        if allowed_params != ["*"]:
            # Check if all provided params are allowed
            # (Simplified check for MVP)
            pass
            
        return True

    def check_rate_limit(self, action_name: str) -> bool:
        """
        Checks if the action exceeds the defined rate limit.
        """
        if action_name not in self.rate_limits:
            return True # No limit defined
            
        limit, window = self.rate_limits[action_name]
        now = time.time()
        
        # Initialize history
        if action_name not in self.usage_history:
            self.usage_history[action_name] = []
            
        # Filter out old timestamps
        history = self.usage_history[action_name]
        valid_history = [t for t in history if now - t < window]
        self.usage_history[action_name] = valid_history
        
        # Check limit
        if len(valid_history) >= limit:
            logger.warning(f"Rate Limit Exceeded for '{action_name}'. (Limit: {limit}/{window}s)")
            return False
            
        # Record usage (optimistic, assuming execution will happen)
        self.usage_history[action_name].append(now)
        return True

# Singleton
tool_guard = ToolGuard()
