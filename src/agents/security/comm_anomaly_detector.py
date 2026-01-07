import logging
import time
from collections import defaultdict
from typing import Dict

logger = logging.getLogger("agent.comm_anomaly")

class CommunicationAnomalyDetector:
    """
    Epic 12.3: Inter-Agent Anomaly Detection.
    Monitors communication patterns between agents to detect compromised or malfunctioning agents.
    """
    
    def __init__(self):
        # Track message counts per agent (rolling window)
        self.message_counts: Dict[str, list] = defaultdict(list)
        
        # Baseline thresholds (messages per minute)
        self.baseline_mpm = {
            "log_ingestion_agent": 100,  # High volume expected
            "mitigation_planning_agent": 10,
            "action_execution_agent": 10,
            "default": 20
        }
        
        # Anomaly multiplier (X times normal)
        self.anomaly_threshold = 5.0
        
        # Time window for analysis (seconds)
        self.time_window = 60.0

    def record_message(self, sender: str):
        """Records a message from an agent."""
        current_time = time.time()
        self.message_counts[sender].append(current_time)
        
        # Clean old messages outside time window
        cutoff = current_time - self.time_window
        self.message_counts[sender] = [
            t for t in self.message_counts[sender] if t > cutoff
        ]

    def check_anomaly(self, sender: str) -> bool:
        """
        Checks if the agent's communication pattern is anomalous.
        Returns True if ANOMALY detected, False if normal.
        """
        current_count = len(self.message_counts[sender])
        baseline = self.baseline_mpm.get(sender, self.baseline_mpm["default"])
        threshold = baseline * self.anomaly_threshold
        
        if current_count > threshold:
            logger.critical(
                f"COMMUNICATION ANOMALY: '{sender}' sent {current_count} msgs/min "
                f"(Baseline: {baseline}, Threshold: {threshold:.0f})"
            )
            return True
            
        return False

# Singleton
comm_anomaly_detector = CommunicationAnomalyDetector()
