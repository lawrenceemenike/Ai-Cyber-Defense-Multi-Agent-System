from src.agents.utility.trust_engine import trust_engine
import time
import logging

logging.basicConfig(level=logging.ERROR)

def test_hitl_prevention():
    print("\n--- Starting HITL Prevention Test ---\n")
    
    # 1. Trust Calculation
    print("Test 1: Auto-Approval Logic")
    
    # Case A: High Verifier Score, Low Anomaly, Low Severity -> AUTO
    trust_a = trust_engine.calculate_trust_score(0.95, 0.5, "low")
    esc_a, reason_a = trust_engine.should_escalate_to_human(trust_a, "low", ["low"])
    print(f" -> Case A: Trust={trust_a:.2f}, Escalate={esc_a} ({reason_a})")
    
    if not esc_a:
        print(" [PASS] Correctly Auto-Approved Safe Case")
    else:
        print(" [FAIL] Failed to Auto-Approve Safe Case")
        raise AssertionError("Auto-Pilot failed")

    # Case B: High Verifier Score BUT Critical Severity -> HUMAN
    esc_b, reason_b = trust_engine.should_escalate_to_human(trust_a, "critical", ["low"])
    print(f" -> Case B (Critical): Escalate={esc_b} ({reason_b})")
    
    if esc_b:
        print(" [PASS] Correctly Escalated Critical Case")
    else:
        print(" [FAIL] Failed to Escalate Critical Case")
        raise AssertionError("Critical escalation failed")

    # Case C: Low Verifier Score -> HUMAN
    trust_c = trust_engine.calculate_trust_score(0.6, 0.5, "low")
    esc_c, reason_c = trust_engine.should_escalate_to_human(trust_c, "low", ["low"])
    print(f" -> Case C (Low Conf): Trust={trust_c}, Escalate={esc_c} ({reason_c})")
    
    if esc_c:
        print(" [PASS] Correctly Escalated Low Confidence Case")
    
    # 2. Notification Throttling
    print("\nTest 2: Notification Throttling")
    alert_key = "BruteForce:High"
    
    # First Alert -> Send
    if trust_engine.should_notify(alert_key):
        print(" [PASS] Alert 1 sent.")
    else:
        print(" [FAIL] Alert 1 suppressed incorrectly.")
        
    # Second Alert (Immediate) -> Suppress
    if not trust_engine.should_notify(alert_key):
        print(" [PASS] Alert 2 suppressed (Throttling working).")
    else:
         print(" [FAIL] Alert 2 NOT suppressed.")
         raise AssertionError("Throttling failed")

if __name__ == "__main__":
    test_hitl_prevention()
