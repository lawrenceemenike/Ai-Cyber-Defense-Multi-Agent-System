import logging
import time
from collections import defaultdict
from typing import Dict, List, Any
import statistics

logger = logging.getLogger("agent.rogue_detector")

class RogueAgentDetector:
    """
    Epic 13.1: Continuous Behavioral Monitoring for Rogue Agents.
    
    Tracks multiple behavioral dimensions per agent:
    - Decision patterns (approve/reject rates)
    - Response timing
    - Output content consistency
    - Action frequency
    
    Flags agents with significant deviation from baseline.
    """
    
    def __init__(self):
        # Behavioral baselines per agent
        self.decision_history: Dict[str, List[str]] = defaultdict(list)
        self.response_times: Dict[str, List[float]] = defaultdict(list)
        self.action_counts: Dict[str, List[int]] = defaultdict(list)
        
        # Thresholds
        self.min_samples = 10  # Need baseline before detection
        self.zscore_threshold = 3.0  # Standard deviations from mean
        
    def record_decision(self, agent_id: str, decision: str):
        """Records an agent's decision (e.g., 'approve', 'reject')."""
        self.decision_history[agent_id].append(decision)
        
    def record_response_time(self, agent_id: str, duration: float):
        """Records how long an agent took to respond."""
        self.response_times[agent_id].append(duration)
        
    def record_action_count(self, agent_id: str, count: int):
        """Records number of actions proposed."""
        self.action_counts[agent_id].append(count)
        
    def detect_anomaly(self, agent_id: str) -> Dict[str, Any]:
        """
        Analyzes agent behavior for anomalies.
        
        Returns:
            Dictionary with anomaly details (empty if none detected)
        """
        anomalies = {}
        
        # 1. Decision Pattern Anomaly
        decisions = self.decision_history[agent_id]
        if len(decisions) >= self.min_samples:
            # Calculate approval rate baseline
            recent_window = decisions[-self.min_samples:]
            approval_rate = sum(1 for d in recent_window if d == 'approve') / len(recent_window)
            
            # Expected baseline (assumes historical ~70% approval)
            if approval_rate < 0.3 or approval_rate > 0.95:
                anomalies['decision_anomaly'] = {
                    'type': 'approval_rate',
                    'value': approval_rate,
                    'expected': '0.6-0.8',
                    'severity': 'high' if approval_rate < 0.1 or approval_rate > 0.99 else 'medium'
                }
                logger.warning(f"ROGUE ALERT: {agent_id} approval rate={approval_rate:.2f} (abnormal)")
        
        # 2. Response Time Anomaly (Z-score)
        times = self.response_times[agent_id]
        if len(times) >= self.min_samples:
            recent_time = times[-1]
            baseline_mean = statistics.mean(times[:-1])
            baseline_std = statistics.stdev(times[:-1]) if len(times) > 2 else 0.1
            
            # Use minimum threshold to avoid division issues with identical values
            baseline_std = max(baseline_std, 0.01)  # Minimum 0.01s std
            z_score = abs((recent_time - baseline_mean) / baseline_std)
            
            if z_score > self.zscore_threshold:
                anomalies['timing_anomaly'] = {
                    'type': 'response_time',
                    'z_score': z_score,
                    'current': recent_time,
                    'baseline_mean': baseline_mean,
                    'severity': 'high' if z_score > 5.0 else 'medium'
                }
                logger.critical(f"ROGUE ALERT: {agent_id} response time Z={z_score:.1f} (abnormal)")
        
        # 3. Action Count Spike
        counts = self.action_counts[agent_id]
        if len(counts) >= self.min_samples:
            recent_count = counts[-1]
            baseline_avg = statistics.mean(counts[:-1])
            
            if recent_count > baseline_avg * 5:  # 5x spike
                anomalies['action_spike'] = {
                    'type': 'action_count',
                    'current': recent_count,
                    'baseline': baseline_avg,
                    'multiplier': recent_count / baseline_avg if baseline_avg > 0 else 0,
                    'severity': 'critical'
                }
                logger.critical(f"ROGUE ALERT: {agent_id} action spike {recent_count} (baseline {baseline_avg:.1f})")
        
        return anomalies

# Singleton
rogue_detector = RogueAgentDetector()
