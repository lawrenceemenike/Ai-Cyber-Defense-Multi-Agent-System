from src.agents.security.rogue_agent_detector import rogue_detector
import logging

logging.basicConfig(level=logging.ERROR)

def test_rogue_detection():
    print("\n--- Starting Rogue Agent Detection Test ---\n")
    
    agent = "mitigation_planning_agent"
    
    # 1. Establish Normal Baseline
    print("Test 1: Establish Baseline (Normal Behavior)")
    # Normal: 70% approval, 1.0s response, 2 actions
    for _ in range(15):
        rogue_detector.record_decision(agent, 'approve' if _ % 10 < 7 else 'reject')
        rogue_detector.record_response_time(agent, 1.0)
        rogue_detector.record_action_count(agent, 2)
    
    anomalies = rogue_detector.detect_anomaly(agent)
    if not anomalies:
        print(" [PASS] Normal baseline established (no anomalies).")
    else:
        print(f" [FAIL] Normal behavior flagged: {anomalies}")
        raise AssertionError("Baseline failed")

    # 2. Decision Pattern Anomaly (Rogue agent suddenly rejects everything)
    print("\nTest 2: Decision Anomaly (100% Rejection Rate)")
    for _ in range(10):
        rogue_detector.record_decision(agent, 'reject')
    
    anomalies = rogue_detector.detect_anomaly(agent)
    if 'decision_anomaly' in anomalies:
        print(f" [PASS] Decision anomaly detected: {anomalies['decision_anomaly']}")
    else:
        print(" [FAIL] Decision anomaly NOT detected.")
        raise AssertionError("Decision anomaly detection failed")

    # 3. Timing Anomaly (Agent becomes very slow - possible DoS)
    print("\nTest 3: Timing Anomaly (10x slower)")
    # Record normal times first
    agent2 = "verifier_agent"
    for _ in range(15):
        rogue_detector.record_response_time(agent2, 1.0)
    
    # Suddenly slow
    rogue_detector.record_response_time(agent2, 10.0)
    
    anomalies = rogue_detector.detect_anomaly(agent2)
    if 'timing_anomaly' in anomalies:
        print(f" [PASS] Timing anomaly detected: Z={anomalies['timing_anomaly']['z_score']:.1f}")
    else:
        print(" [FAIL] Timing anomaly NOT detected.")
        raise AssertionError("Timing anomaly detection failed")

    # 4. Action Spike (Agent proposes many actions - possible spam attack)
    print("\nTest 4: Action Spike (20x increase)")
    agent3 = "action_execution_agent"
    for _ in range(15):
        rogue_detector.record_action_count(agent3, 2)
    
    rogue_detector.record_action_count(agent3, 40)  # 20x spike
    
    anomalies = rogue_detector.detect_anomaly(agent3)
    if 'action_spike' in anomalies:
        print(f" [PASS] Action spike detected: {anomalies['action_spike']['multiplier']:.1f}x")
    else:
        print(" [FAIL] Action spike NOT detected.")
        raise AssertionError("Action spike detection failed")

if __name__ == "__main__":
    test_rogue_detection()
