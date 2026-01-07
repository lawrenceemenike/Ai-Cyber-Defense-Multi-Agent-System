from src.agents.security.loop_detector import loop_detector
import logging

logging.basicConfig(level=logging.ERROR)

def test_loop_detection():
    print("\n--- Starting Loop Detection Test ---\n")
    
    req_id = "req_infinite_loop"
    loop_detector.clear(req_id)
    
    # 1. Total Depth Limit
    print("Test 1: Total Steps Exceeded")
    allowed = True
    for i in range(12): # Max is 10
        if not loop_detector.track_step(req_id, f"step_{i}"):
            allowed = False
            print(f" [PASS] Loop detected at step {i+1} (Max 10)")
            break
            
    if allowed:
        print(" [FAIL] Failed to detect depth limit.")
        raise AssertionError("Depth limit detection failed")
        
    # 2. Oscillation Limit
    print("\nTest 2: Oscillation (A->B->A->B...)")
    req_osc = "req_oscillation"
    loop_detector.clear(req_osc)
    
    nodes = ["planner", "verifier", "planner", "verifier", "planner", "verifier", "planner"] 
    # planner appears 4 times (limit 3)
    
    allowed_osc = True
    for node in nodes:
        if not loop_detector.track_step(req_osc, node):
            allowed_osc = False
            print(f" [PASS] Oscillation detected at '{node}'")
            break
            
    if allowed_osc:
        print(" [FAIL] Failed to detect oscillation.")
        raise AssertionError("Oscillation detection failed")

if __name__ == "__main__":
    test_loop_detection()
