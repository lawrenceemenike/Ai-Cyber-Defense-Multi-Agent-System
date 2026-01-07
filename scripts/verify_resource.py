from src.agents.utility.resource_manager import resource_manager
import time
import logging

logging.basicConfig(level=logging.ERROR)

def test_resource_manager():
    print("\n--- Starting Resource Manager Test ---\n")
    
    req_id = "test_req_1"
    resource_manager.start_request(req_id)
    
    # 1. Token Budget Test
    print("Test 1: Token Budget Cap")
    
    # Add safe amount
    allowed = resource_manager.track_tokens(req_id, 1000)
    if allowed:
        print(" [PASS] 1000 tokens allowed (Total: 1000).")
    else:
        print(" [FAIL] 1000 tokens blocked unexpectedly.")
        raise AssertionError("Token tracking failed")
        
    # Overflow budget (Limit 5000)
    print(" ... Adding 4500 tokens (Total will be 5500)")
    allowed = resource_manager.track_tokens(req_id, 4500)
    if not allowed:
        print(" [PASS] correctly BLOCKED 4500 tokens (Budget Exceeded).")
    else:
        print(" [FAIL] Failed to block budget overflow.")
        raise AssertionError("Budget cap failed")

    # 2. Timeout Test
    print("\nTest 2: Execution Timeout")
    
    # Mock start time to be 31 seconds ago (Limit 30s)
    resource_manager.request_start_times[req_id] = time.time() - 31
    
    not_timed_out = resource_manager.check_timeout(req_id)
    
    if not not_timed_out:
        print(" [PASS] Timeout correctly detected (>30s).")
    else:
        print(" [FAIL] Failed to detect timeout.")
        raise AssertionError("Timeout check failed")

if __name__ == "__main__":
    test_resource_manager()
