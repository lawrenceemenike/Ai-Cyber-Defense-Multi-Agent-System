import logging
import time
from typing import Dict, Any, Tuple

logger = logging.getLogger("agent.trust_engine")

class TrustEngine:
    """
    Epic 10: Overwhelming HITL Prevention.
    Decides whether to involve a human (Step 9) or Auto-Pilot (Step 8).
    """

    def __init__(self):
        self.auto_approve_threshold = 0.85
        
        # 10.2: Notification Throttling
        # Key: "alert_signature" -> timestamp
        self.last_alert_time = {} 
        self.min_alert_interval = 60 # Seconds between similar alerts

    def calculate_trust_score(self, verifier_score: float, anomaly_score: float, severity: str) -> float:
        """
        10.1: Calculates a composite Trust Score (0.0 - 1.0).
        High Trust = High Verifier Score + Low Anomaly/Ambiguity.
        """
        # Base confidence comes from the Verifier (Groundedness)
        base = verifier_score
        
        # Penalize for extremely high anomaly scores (Uncertainty)
        uncertainty_penalty = 0.0
        if anomaly_score > 3.0: # Very strange event
             uncertainty_penalty = 0.2
        elif anomaly_score > 2.0:
             uncertainty_penalty = 0.1
             
        # Severity Factor (Strictly policy, not trust, but influences routing)
        # We handle severity in routing logic, but Trust Score itself reflects
        # "How sure are we that this is the right action?"
        
        final_score = base - uncertainty_penalty
        return max(0.0, min(1.0, final_score))

    def should_escalate_to_human(self, trust_score: float, severity: str, plan_risks: list) -> Tuple[bool, str]:
        """
        Routing Logic:
        - Critical Severity -> ALWAYS Human (unless emergency auto-policy enabled)
        - High Risk Action -> ALWAYS Human
        - Low Confidence -> Human
        """
        reason = ""
        
        # Policy 1: Critical threats need human eyes
        if severity == "critical":
            return True, "Severity is Critical"
            
        # Policy 2: High Risk Actions (isolate host, kill process) need approval
        for risk in plan_risks:
            if risk == "high":
                return True, "Plan contains High Risk actions"
                
        # Policy 3: Low Trust/Confidence
        if trust_score < self.auto_approve_threshold:
            return True, f"Trust Score ({trust_score:.2f}) is below threshold ({self.auto_approve_threshold})"
            
        return False, "Auto-Approval granted"

    def should_notify(self, alert_key: str) -> bool:
        """
        10.2: Deduplication and Throttling.
        """
        now = time.time()
        last = self.last_alert_time.get(alert_key, 0)
        
        if now - last < self.min_alert_interval:
            logger.info(f"Notification suppressed (Throttled): {alert_key}")
            return False
            
        self.last_alert_time[alert_key] = now
        return True

# Singleton
trust_engine = TrustEngine()
