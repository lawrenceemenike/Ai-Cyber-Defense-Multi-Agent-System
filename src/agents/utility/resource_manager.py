import logging
import time
from typing import Dict, Any

logger = logging.getLogger("agent.resource_manager")

class ResourceManager:
    """
    Epic 4: Resource Overload Prevention.
    Manages Token Budgets, Timeouts, and API Rate limits.
    """
    
    def __init__(self):
        # 4.1: Hard Budget Caps
        self.max_tokens_per_request = 5000
        self.max_execution_time_sec = 30.0 # Strict timeout for MVP
        
        # Tracking
        self.request_start_times = {}
        self.request_token_usage = {}

    def start_request(self, request_id: str):
        """Register start of a request."""
        self.request_start_times[request_id] = time.time()
        self.request_token_usage[request_id] = 0

    def track_tokens(self, request_id: str, tokens: int) -> bool:
        """
        Accumulate token usage. Returns False if budget exceeded.
        """
        current = self.request_token_usage.get(request_id, 0)
        new_total = current + tokens
        self.request_token_usage[request_id] = new_total
        
        if new_total > self.max_tokens_per_request:
            logger.error(f"Resource Budget Exceeded: {new_total} tokens (Limit: {self.max_tokens_per_request})")
            return False
        return True

    def check_timeout(self, request_id: str) -> bool:
        """
        Returns False if execution time limit exceeded.
        """
        start_time = self.request_start_times.get(request_id)
        if not start_time:
            return True # Not tracking?
            
        elapsed = time.time() - start_time
        if elapsed > self.max_execution_time_sec:
            logger.error(f"Timeout Exceeded: {elapsed:.2f}s (Limit: {self.max_execution_time_sec}s)")
            return False
            
        return True

    def get_stats(self, request_id: str) -> Dict[str, Any]:
        return {
            "tokens": self.request_token_usage.get(request_id, 0),
            "elapsed": time.time() - self.request_start_times.get(request_id, 0)
        }

# Singleton
resource_manager = ResourceManager()
