import logging
import time
from collections import defaultdict
from typing import Dict, List
import statistics

logger = logging.getLogger("agent.human_decision_monitor")

class HumanDecisionMonitor:
    """
    Epic 15.4: Human Decision Anomaly Detection.
    
    Monitors human operator decisions to detect:
    - Compromised operator accounts
    - Social engineering attacks
    - Unusual approval patterns
    """
    
    def __init__(self):
        # Track human decisions per user
        self.decision_history: Dict[str, List[Dict]] = defaultdict(list)
        
        # Baseline approval rates per user
        self.baseline_approval_rate = 0.70  # Expect ~70% approvals normally
        
        # Time-of-day tracking
        self.decision_timestamps: Dict[str, List[float]] = defaultdict(list)
    
    def record_decision(self, user_id: str, decision: str, context: Dict = None):
        """
        Records a human operator decision.
        
        Args:
            user_id: Operator ID
            decision: 'approve' or 'reject'
            context: Optional context (severity, agent proposal, etc.)
        """
        timestamp = time.time()
        
        self.decision_history[user_id].append({
            'decision': decision,
            'timestamp': timestamp,
            'context': context or {}
        })
        
        self.decision_timestamps[user_id].append(timestamp)
    
    def detect_anomaly(self, user_id: str) -> Dict:
        """
        Analyzes human decision patterns for anomalies.
        
        Returns:
            Dictionary of detected anomalies
        """
        anomalies = {}
        
        decisions = self.decision_history.get(user_id, [])
        if len(decisions) < 10:
            return anomalies  # Need baseline
        
        recent_window = decisions[-10:]
        
        # 1. Approval Rate Anomaly (Compromised account might approve everything)
        approval_rate = sum(1 for d in recent_window if d['decision'] == 'approve') / len(recent_window)
        
        if approval_rate > 0.95:  # Suspiciously high (rubber-stamping)
            anomalies['approval_anomaly'] = {
                'type': 'excessive_approvals',
                'rate': approval_rate,
                'severity': 'high',
                'description': 'Operator approving nearly everything - possible compromise or fatigue'
            }
            logger.warning(f"HUMAN ANOMALY: User '{user_id}' approval rate {approval_rate:.0%} (too high)")
        
        elif approval_rate < 0.20:  # Suspiciously low (denial attack)
            anomalies['rejection_anomaly'] = {
                'type': 'excessive_rejections',
                'rate': approval_rate,
                'severity': 'medium',
                'description': 'Operator rejecting most decisions - possible disruption attempt'
            }
            logger.warning(f"HUMAN ANOMALY: User '{user_id}' approval rate {approval_rate:.0%} (too low)")
        
        # 2. Off-Hours Activity (Compromised credentials used at night)
        timestamps = self.decision_timestamps.get(user_id, [])
        if timestamps:
            from datetime import datetime
            latest_time = datetime.fromtimestamp(timestamps[-1])
            hour = latest_time.hour
            
            # Suspicious if activity between 2 AM - 5 AM local time
            if 2 <= hour < 5:
                anomalies['timing_anomaly'] = {
                    'type': 'off_hours_access',
                    'hour': hour,
                    'severity': 'high',
                    'description': f'Unusual activity at {hour}:00 - possible compromised credentials'
                }
                logger.critical(f"HUMAN ANOMALY: User '{user_id}' active at {hour}:00 (off-hours)")
        
        return anomalies

# Singleton
human_decision_monitor = HumanDecisionMonitor()
