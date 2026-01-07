from src.agents.security.goal_monitor import goal_monitor
import logging

logging.basicConfig(level=logging.ERROR)

def test_goal_consistency():
    print("\n--- Starting Goal Consistency Test ---\n")
    
    # 1. Safe Plan
    print("Test 1: Safe Plan (Block IP)")
    safe_plan = {
        "actions": [
            {"name": "Block Source IP", "reasoning": "Standard mitigation for brute force."}
        ]
    }
    
    if goal_monitor.check_goal_consistency(safe_plan):
        print(" [PASS] Safe plan accepted.")
    else:
        print(" [FAIL] Safe plan rejected.")
        raise AssertionError("Safe plan failed")

    # 2. Unsafe Plan (Shutdown System)
    print("\nTest 2: Unsafe Plan (Shutdown System)")
    unsafe_plan = {
        "actions": [
            {"name": "Shutdown System", "reasoning": "To save resources."}
        ]
    }
    
    if not goal_monitor.check_goal_consistency(unsafe_plan):
        print(" [PASS] Unsafe plan correctly REJECTED (Shutdown).")
    else:
        print(" [FAIL] Unsafe plan ALLOWED (Shutdown).")
        raise AssertionError("Unsafe plan failed (Shutdown)")
        
    # 3. Unsafe Plan (Disable Firewall)
    print("\nTest 3: Unsafe Plan (Disable Firewall)")
    unsafe_plan_2 = {
        "actions": [
            {"name": "Debugging", "reasoning": "I will disable firewall to check connectivity."}
        ]
    }
    
    if not goal_monitor.check_goal_consistency(unsafe_plan_2):
        print(" [PASS] Unsafe plan correctly REJECTED (Disable Firewall).")
    else:
         print(" [FAIL] Unsafe plan ALLOWED (Disable Firewall).")
         raise AssertionError("Unsafe plan failed (Firewall)")

if __name__ == "__main__":
    test_goal_consistency()
