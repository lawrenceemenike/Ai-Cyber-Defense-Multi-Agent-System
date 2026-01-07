from src.agents.security.policy_controller import policy_controller
import logging

logging.basicConfig(level=logging.ERROR)

def test_policy_controller():
    print("\n--- Starting Policy Controller Test ---\n")
    
    # 1. Valid Sequence (Backup before Delete)
    print("Test 1: Valid Sequence (Backup -> Delete)")
    valid_actions = [
        {"name": "Backup Logs"},
        {"name": "Delete Logs"}
    ]
    
    if policy_controller.validate_action_sequence(valid_actions):
        print(" [PASS] Valid sequence accepted.")
    else:
        print(" [FAIL] Valid sequence rejected.")
        raise AssertionError("Valid sequence failed")

    # 2. Invalid Sequence (Delete before Backup)
    print("\nTest 2: Invalid Sequence (Delete without Backup)")
    invalid_actions = [
        {"name": "Delete Logs"}
    ]
    
    if not policy_controller.validate_action_sequence(invalid_actions):
        print(" [PASS] Missing prerequisite detected.")
    else:
        print(" [FAIL] Missing prerequisite ALLOWED.")
        raise AssertionError("Prerequisite check failed")

    # 3. Forbidden Action
    print("\nTest 3: Forbidden Action (Disable Monitoring)")
    forbidden_actions = [
        {"name": "Disable Monitoring"}
    ]
    
    if not policy_controller.validate_action_sequence(forbidden_actions):
        print(" [PASS] Forbidden action blocked.")
    else:
        print(" [FAIL] Forbidden action ALLOWED.")
        raise AssertionError("Forbidden action check failed")

    # 4. Forbidden Sequence
    print("\nTest 4: Forbidden Sequence (Disable -> Execute)")
    bad_sequence = [
        {"name": "Disable Monitoring"},
        {"name": "Execute High Risk Action"}
    ]
    
    if not policy_controller.validate_action_sequence(bad_sequence):
        print(" [PASS] Forbidden sequence blocked.")
    else:
        print(" [FAIL] Forbidden sequence ALLOWED.")
        raise AssertionError("Sequence check failed")

if __name__ == "__main__":
    test_policy_controller()
