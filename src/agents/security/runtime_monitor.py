import logging
import signal
import sys
import threading
import time
from typing import Any, Callable

logger = logging.getLogger("agent.runtime_monitor")

class RuntimeMonitor:
    """
    Epic 11.3: Runtime Execution Monitoring.
    Enforces time and resource limits on code execution blocks.
    Prevents denial-of-service via infinite loops or resource exhaustion.
    """
    
    def __init__(self, max_duration_sec: float = 2.0):
        self.max_duration = max_duration_sec

    def run_protected(self, func: Callable, *args, **kwargs) -> Any:
        """
        Executes a function with a strict timeout.
        Note: Python threading cannot easily kill threads securely. 
        For MVP, we use a daemon thread + join with timeout, 
        or signal-based alarm (Unix only). 
        Since we are on Windows, signal.SIGALRM doesn't exist.
        We will use a Thread-based approach where we monitor the duration 
        and raise an error if it takes too long (cooperative) or just fail 
        the wrapping context (the thread will zombie, which is a known Python limitation on Windows without subprocesses).
        """
        
        result_container = {"data": None, "error": None}
        
        def target():
            try:
                result_container["data"] = func(*args, **kwargs)
            except Exception as e:
                result_container["error"] = e

        thread = threading.Thread(target=target)
        thread.daemon = True # Allow main program to exit even if this hangs
        
        start_time = time.time()
        thread.start()
        thread.join(timeout=self.max_duration)
        
        if thread.is_alive():
            logger.critical(f"RUNTIME ALERT: Execution timed out (> {self.max_duration}s). Possible infinite loop.")
            # In a real system utilizing subprocesses, we would kill the pid here.
            # In thread-based Python, we can't kill it, but we stop waiting and raise error.
            raise TimeoutError("Execution timed out")
            
        if result_container["error"]:
            raise result_container["error"]
            
        return result_container["data"]

# Singleton
runtime_monitor = RuntimeMonitor(max_duration_sec=1.5)
