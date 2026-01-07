from src.agents.security.comm_anomaly_detector import comm_anomaly_detector
import logging

logging.basicConfig(level=logging.ERROR)

def test_communication_anomaly():
    print("\n--- Starting Communication Anomaly Detection Test ---\n")
    
    agent = "mitigation_planning_agent"
    
    # 1. Normal Traffic
    print("Test 1: Normal Traffic (5 messages)")
    for _ in range(5):
        comm_anomaly_detector.record_message(agent)
    
    if not comm_anomaly_detector.check_anomaly(agent):
        print(f" [PASS] Normal traffic (5 msgs) accepted.")
    else:
        print(" [FAIL] Normal traffic flagged as anomaly.")
        raise AssertionError("Normal traffic failed")

    # 2. Anomalous Traffic (Burst Attack)
    print("\nTest 2: Anomalous Traffic (60 messages - 6x baseline of 10)")
    for _ in range(55):  # Already have 5 from test 1
        comm_anomaly_detector.record_message(agent)
    
    if comm_anomaly_detector.check_anomaly(agent):
        print(f" [PASS] Burst traffic correctly flagged (60 msgs > 50 threshold).")
    else:
        print(" [FAIL] Burst traffic NOT detected.")
        raise AssertionError("Anomaly detection failed")

if __name__ == "__main__":
    test_communication_anomaly()
