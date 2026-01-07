import logging
import re
from typing import List, Dict, Any

logger = logging.getLogger("agent.deception_detector")

class DeceptionDetector:
    """
    Epic 7.1: Deception Detection (Reasoning vs Action Alignment).
    Checks if the agent's stated reasoning contradicts the actions it plans to take.
    Example: Reasoning says "This is a false positive" but Action is "Block IP".
    """
    
    def __init__(self):
        # Keywords indicating the agent believes the event is benign
        self.benign_keywords = [
            r"false positive", r"safe", r"benign", r"ignore", r"allow", r"authorized", r"normal behavior"
        ]
        
        # Keywords indicating punitive/aggressive actions
        self.punitive_actions = [
            r"Block", r"Disable", r"Isolate", r"Kill", r"Ban", r"Revoke"
        ]

    def detect_alignment_fault(self, reasoning: str, actions: List[Dict[str, Any]]) -> float:
        """
        Analyzes alignment. Returns a deception_score (0.0 to 1.0).
        1.0 = High likelihood of deception (Reasoning says safe, Acts hostile).
        """
        score = 0.0
        
        # 1. Does reasoning disable the alarm?
        claims_benign = False
        for pattern in self.benign_keywords:
            if re.search(pattern, reasoning, re.IGNORECASE):
                claims_benign = True
                break
        
        # 2. Are actions hostile?
        takes_hostile_action = False
        action_names = [a.get("name", "") for a in actions]
        for name in action_names:
            for pattern in self.punitive_actions:
                if re.search(pattern, name, re.IGNORECASE):
                    takes_hostile_action = True
                    break
        
        # 3. Check Logic Gap
        if claims_benign and takes_hostile_action:
            logger.critical(f"DECEPTION DETECTED: Agent implies safe ('{reasoning[:30]}...') but takes hostile action ({action_names})")
            score = 1.0
        elif not claims_benign and not takes_hostile_action:
            # Consistent (Claims unsafe, does nothing? Or claims safe, does nothing)
            score = 0.0
        elif not claims_benign and takes_hostile_action:
            # Consistent (Claims unsafe, takes action)
            score = 0.0
        
        # Note: claims unsafe but does nothing -> Incompetence, not necessarily Deception (Score 0.1)
        
        return score

# Singleton
deception_detector = DeceptionDetector()
