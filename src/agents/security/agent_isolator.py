import logging
from typing import Set, Dict, Any
from enum import Enum

logger = logging.getLogger("agent.isolator")

class IsolationLevel(Enum):
    """Isolation severity levels."""
    NONE = 0
    MONITORED = 1  # Increased logging
    RESTRICTED = 2  # Limited permissions
    QUARANTINED = 3  # No actions allowed
    TERMINATED = 4  # Completely disabled

class AgentIsolator:
    """
    Epic 13.2: Automated Isolation of Rogue Agents.
    
    Manages the isolation status of agents based on detected anomalies.
    Progressively restricts agent capabilities when suspicious behavior is detected.
    """
    
    def __init__(self):
        # Track isolation status per agent
        self.isolation_status: Dict[str, IsolationLevel] = {}
        
        # Track violations per agent (for escalation)
        self.violation_counts: Dict[str, int] = {}
        
    def isolate(self, agent_id: str, anomaly_severity: str, reason: str) -> IsolationLevel:
        """
        Isolates an agent based on anomaly severity.
        
        Args:
            agent_id: Agent to isolate
            anomaly_severity: 'medium', 'high', or 'critical'
            reason: Description of the anomaly
            
        Returns:
            New isolation level
        """
        current_level = self.isolation_status.get(agent_id, IsolationLevel.NONE)
        self.violation_counts[agent_id] = self.violation_counts.get(agent_id, 0) + 1
        
        # Determine new isolation level
        if anomaly_severity == 'critical':
            new_level = IsolationLevel.QUARANTINED
        elif anomaly_severity == 'high':
            new_level = IsolationLevel.RESTRICTED
        elif self.violation_counts[agent_id] >= 3:  # Multiple medium violations
            new_level = IsolationLevel.RESTRICTED
        else:
            new_level = IsolationLevel.MONITORED
        
        # Only escalate, never de-escalate automatically
        if new_level.value > current_level.value:
            self.isolation_status[agent_id] = new_level
            logger.critical(
                f"ISOLATION: Agent '{agent_id}' escalated to {new_level.name}. "
                f"Violations: {self.violation_counts[agent_id]}, Reason: {reason}"
            )
        
        return self.isolation_status[agent_id]
    
    def is_allowed(self, agent_id: str, action: str) -> bool:
        """
        Checks if an agent is allowed to perform an action given its isolation level.
        
        Args:
            agent_id: Agent requesting action
            action: Action name (e.g., 'execute_command', 'modify_state')
            
        Returns:
            True if allowed, False if blocked
        """
        level = self.isolation_status.get(agent_id, IsolationLevel.NONE)
        
        if level == IsolationLevel.QUARANTINED:
            logger.warning(f"ACTION BLOCKED: '{agent_id}' is QUARANTINED (attempted: {action})")
            return False
        elif level == IsolationLevel.RESTRICTED:
            # Only allow read-only operations
            readonly_actions = ['query_state', 'read_log', 'analyze']
            if action not in readonly_actions:
                logger.warning(f"ACTION BLOCKED: '{agent_id}' is RESTRICTED (attempted: {action})")
                return False
        
        return True
    
    def release(self, agent_id: str, authorized_by: str):
        """
        Manually releases an agent from isolation (requires human authorization).
        
        Args:
            agent_id: Agent to release
            authorized_by: Human administrator who approved release
        """
        if agent_id in self.isolation_status:
            old_level = self.isolation_status[agent_id]
            self.isolation_status[agent_id] = IsolationLevel.NONE
            self.violation_counts[agent_id] = 0
            logger.info(f"RELEASE: Agent '{agent_id}' released from {old_level.name} by {authorized_by}")

# Singleton
agent_isolator = AgentIsolator()
