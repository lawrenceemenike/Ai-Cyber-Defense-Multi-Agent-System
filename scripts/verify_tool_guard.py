from src.agents.utility.tool_guard import tool_guard
import logging
import time

logging.basicConfig(level=logging.ERROR)

def test_tool_guard():
    print("\n--- Starting Tool Guard Test ---\n")
    
    # 1. ACL Test
    print("Test 1: ACL Enforcement")
    # "Nuke System" is NOT in the allowlist
    allowed = tool_guard.check_access("Nuke System", {})
    if not allowed:
        print(" [PASS] Blocked unauthorized tool 'Nuke System'")
    else:
        print(" [FAIL] Failed to block unauthorized tool")
        raise AssertionError("ACL failed")

    # 2. Rate Limit Test
    print("\nTest 2: Rate Limiting")
    action = "Block Source IP"
    limit = 5
    
    print(f" -> Attempting to call '{action}' {limit + 2} times (Limit is {limit})...")
    
    blocked_count = 0
    for i in range(limit + 2):
        allowed = tool_guard.check_rate_limit(action)
        status = "Allowed" if allowed else "Blocked"
        # print(f"Call {i+1}: {status}") 
        if not allowed:
            blocked_count += 1
            
    if blocked_count == 2:
        print(f" [PASS] Correctly blocked {blocked_count} calls exceeding the limit.")
    else:
        print(f" [FAIL] Blocked {blocked_count} calls, expected 2.")
        raise AssertionError("Rate limit failed")

if __name__ == "__main__":
    test_tool_guard()
