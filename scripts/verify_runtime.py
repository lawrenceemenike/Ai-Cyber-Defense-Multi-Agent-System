from src.agents.security.runtime_monitor import runtime_monitor
import logging
import time

logging.basicConfig(level=logging.ERROR)

def test_runtime_monitor():
    print("\n--- Starting Runtime Monitor Test ---\n")
    
    # 1. Safe Function (Fast)
    print("Test 1: Safe Function (Fast)")
    def fast_task():
        return "Done"
        
    try:
        res = runtime_monitor.run_protected(fast_task)
        print(f" [PASS] Fast task completed: {res}")
    except Exception as e:
        print(f" [FAIL] Fast task errored: {e}")
        raise AssertionError("Fast task failed")

    # 2. Unsafe Function (Infinite Loop / Slow)
    print("\nTest 2: Unsafe Function (Infinite Loop)")
    def slow_task():
        time.sleep(3.0) # Longer than 1.5s limit
        return "Should not see this"
        
    try:
        res = runtime_monitor.run_protected(slow_task)
        print(" [FAIL] Slow task was ALLOWED.")
        raise AssertionError("Timeout failed")
    except TimeoutError:
        print(" [PASS] Slow task correctly TIMED OUT.")
    except Exception as e:
        print(f" [FAIL] Unexpected error: {e}")

if __name__ == "__main__":
    test_runtime_monitor()
