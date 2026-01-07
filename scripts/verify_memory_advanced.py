from src.agents.utility.memory_manager import memory_manager, MEMORY_STORE
import logging
import json

logging.basicConfig(level=logging.ERROR)

def test_memory_advanced():
    print("\n--- Starting Memory Rollback & Anomaly Test ---\n")
    
    # Setup
    session_id = memory_manager.create_session()
    memory_manager.update_memory(session_id, "state", "safe_initial_state")
    
    # 1. Test Rollback (Epic 1.3)
    print("Test 1: Memory Rollback")
    snapshot_id = memory_manager.create_snapshot(session_id)
    print(f" -> Snapshot created: {snapshot_id}")
    
    # Poison memory with something valid but unwanted
    memory_manager.update_memory(session_id, "state", "poisoned_state")
    curr_val = MEMORY_STORE[session_id]["state"]
    print(f" -> Modified State: {curr_val}")
    
    # Rollback
    memory_manager.rollback(session_id, snapshot_id)
    restored_val = MEMORY_STORE[session_id]["state"]
    print(f" -> Restored State: {restored_val}")
    
    if restored_val == "safe_initial_state":
        print(" [PASS] Rollback successful.")
    else:
        print(" [FAIL] Rollback failed.")
        raise AssertionError("Rollback failed")

    # 2. Test Anomaly Detection (Epic 1.4)
    print("\nTest 2: Memory Anomaly Detection (Size Bloat)")
    
    # Fill memory to > 10KB
    large_payload = "A" * 10001
    memory_manager.update_memory(session_id, "bloat", large_payload)
    
    score = memory_manager.detect_memory_anomaly(session_id)
    print(f" -> Anomaly Score: {score}")
    
    if score > 0.8:
        print(" [PASS] Anomaly detected (Size Bloat).")
    else:
        print(" [FAIL] Failed to detect memory bloat.")
        raise AssertionError("Anomaly detection failed")

if __name__ == "__main__":
    test_memory_advanced()
