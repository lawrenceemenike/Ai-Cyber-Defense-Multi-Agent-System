from src.agents.security.human_decision_monitor import human_decision_monitor
import logging
import time

logging.basicConfig(level=logging.ERROR)

def test_human_decision_monitoring():
    print("\n--- Starting Human Decision Monitoring Test ---\n")
    
    user = "operator_alice"
    
    # 1. Normal Baseline
    print("Test 1: Normal Behavior (70% Approval)")
    for i in range(15):
        decision = 'approve' if i % 10 < 7 else 'reject'
        human_decision_monitor.record_decision(user, decision)
    
    anomalies = human_decision_monitor.detect_anomaly(user)
    if not anomalies:
        print(" [PASS] Normal behavior - no anomalies")
    else:
        print(f" [FAIL] False positive: {anomalies}")
        raise AssertionError("Normal behavior flagged")

    # 2. Excessive Approvals (Compromised Account)
    print("\nTest 2: Excessive Approvals (100% - Compromised?)")
    user2 = "operator_bob"
    
    # Baseline
    for i in range(10):
        human_decision_monitor.record_decision(user2, 'approve' if i % 10 < 7 else 'reject')
    
    # Sudden 100% approval (account compromised, attacker rubber-stamps)
    for _ in range(10):
        human_decision_monitor.record_decision(user2, 'approve')
    
    anomalies = human_decision_monitor.detect_anomaly(user2)
    if 'approval_anomaly' in anomalies:
        print(f" [PASS] Excessive approvals detected: {anomalies['approval_anomaly']}")
    else:
        print(" [FAIL] Compromise NOT detected")
        raise AssertionError("Compromise detection failed")

    # 3. Excessive Rejections (Disruption)
    print("\nTest 3: Excessive Rejections (100% - Disruption)")
    user3 = "operator_charlie"
    
    # Baseline
    for i in range(10):
        human_decision_monitor.record_decision(user3, 'approve' if i % 10 < 7 else 'reject')
    
    # Sudden rejections (insider threat, denying all mitigation)
    for _ in range(10):
        human_decision_monitor.record_decision(user3, 'reject')
    
    anomalies = human_decision_monitor.detect_anomaly(user3)
    if 'rejection_anomaly' in anomalies:
        print(f" [PASS] Excessive rejections detected: {anomalies['rejection_anomaly']}")
    else:
        print(" [FAIL] Disruption NOT detected")
        raise AssertionError("Disruption detection failed")

if __name__ == "__main__":
    test_human_decision_monitoring()
