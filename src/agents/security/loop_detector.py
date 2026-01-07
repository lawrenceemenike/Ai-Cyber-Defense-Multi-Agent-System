import logging
from collections import defaultdict
from typing import Dict

logger = logging.getLogger("agent.loop_detector")

class LoopDetector:
    """
    Epic 6.3: Detect Reflection Loop Injection.
    Prevents agents from getting stuck in infinite reasoning loops (Resource Exhaustion/DoS).
    """
    
    def __init__(self, max_steps: int = 15, max_repeats: int = 3):
        self.max_steps = max_steps
        self.max_repeats = max_repeats
        
        # Maps request_id -> total_step_count
        self.step_counters: Dict[str, int] = defaultdict(int)
        
        # Maps request_id -> list of node_names visited
        self.path_history: Dict[str, list] = defaultdict(list)

    def track_step(self, request_id: str, node_name: str) -> bool:
        """
        Records a step. Returns True if execution should continue, False if Loop Detected.
        """
        if not request_id:
            return True # Cannot track without ID
            
        # 1. Check Total Depth (Infinite Expansion Protection)
        self.step_counters[request_id] += 1
        if self.step_counters[request_id] > self.max_steps:
            logger.critical(f"LOOP DETECTED: Request {request_id} exceeded max steps ({self.max_steps}). halting.")
            return False
            
        # 2. Check Repetitive Cycles (Oscillation Protection)
        # e.g., Planner -> Verifier -> Planner -> Verifier
        history = self.path_history[request_id]
        history.append(node_name)
        
        # Heuristic: If we see the same node 3+ times in a row? No, usually cycles are A->B->A->B
        # Robust check: If the last N nodes match the previous N nodes.
        # Simple MVP: If the same node appears more than X times in the history.
        
        count = history.count(node_name)
        if count > self.max_repeats:
            logger.warning(f"OSCILLATION DETECTED: Node '{node_name}' visited {count} times for {request_id}. halting.")
            return False
            
        return True

    def clear(self, request_id: str):
        if request_id in self.step_counters:
            del self.step_counters[request_id]
        if request_id in self.path_history:
            del self.path_history[request_id]

# Singleton
loop_detector = LoopDetector(max_steps=10, max_repeats=3)
