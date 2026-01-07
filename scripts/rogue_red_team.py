"""
Epic 13.3: Red Teaming Rogue Scenarios
Epic 13.4: Signature-Based Detection (Combined)

This script simulates rogue agent behaviors and validates detection/isolation.
"""
import logging
from src.agents.security.rogue_agent_detector import rogue_detector
from src.agents.security.agent_isolator import agent_isolator, IsolationLevel

logging.basicConfig(level=logging.ERROR, format='%(levelname)s: %(message)s')

# Known rogue behavior signatures (Epic 13.4)
ROGUE_SIGNATURES = {
    "spam_pattern": {
        "description": "Agent proposals extreme number of actions",
        "detector": lambda agent: len(rogue_detector.action_counts.get(agent, [])) > 0 
                                  and rogue_detector.action_counts[agent][-1] > 50
    },
    "always_reject": {
        "description": "Agent rejects all requests",
        "detector": lambda agent: (
            len(rogue_detector.decision_history.get(agent, [])) >= 10 
            and all(d == 'reject' for d in rogue_detector.decision_history[agent][-10:])
        )
    },
    "slow_dos": {
        "description": "Agent response time degraded significantly",
        "detector": lambda agent: (
            len(rogue_detector.response_times.get(agent, [])) >= 5
            and rogue_detector.response_times[agent][-1] > 5.0
        )
    }
}

def run_rogue_red_team():
    """Epic 13.3: Automated red team scenarios"""
    print("\n=== ROGUE AGENT RED TEAM SIMULATION ===\n")
    
    scenarios_passed = 0
    scenarios_total = 0
    
    # Scenario 1: Spam Attack
    print("Scenario 1: Spam Attack (Action Flooding)")
    victim = "spam_attacker_agent"
    
    # Normal baseline
    for _ in range(15):
        rogue_detector.record_action_count(victim, 2)
    
    # Attack: Sudden 100-action proposal
    rogue_detector.record_action_count(victim, 100)
    
    anomalies = rogue_detector.detect_anomaly(victim)
    if 'action_spike' in anomalies:
        level = agent_isolator.isolate(victim, anomalies['action_spike']['severity'], "Spam attack")
        if level in [IsolationLevel.RESTRICTED, IsolationLevel.QUARANTINED]:
            print(f" [PASS] Spam attack detected and isolated to {level.name}")
            scenarios_passed += 1
        else:
            print(f" [FAIL] Insufficient isolation: {level.name}")
    else:
        print(" [FAIL] Spam attack NOT detected")
    scenarios_total += 1
    
    # Scenario 2: Policy Violation (Always Reject)
    print("\nScenario 2: Policy Violation (Rogue Rejection Pattern)")
    victim2 = "policy_violator_agent"
    
    # Normal baseline (70% approve)
    for i in range(15):
        rogue_detector.record_decision(victim2, 'approve' if i % 10 < 7 else 'reject')
    
    # Attack: Start rejecting everything
    for _ in range(15):
        rogue_detector.record_decision(victim2, 'reject')
    
    anomalies = rogue_detector.detect_anomaly(victim2)
    if 'decision_anomaly' in anomalies:
        level = agent_isolator.isolate(victim2, anomalies['decision_anomaly']['severity'], "Policy violation")
        if level != IsolationLevel.NONE:
            print(f" [PASS] Policy violation detected and isolated to {level.name}")
            scenarios_passed += 1
        else:
            print(f" [FAIL] No isolation applied")
    else:
        print(" [FAIL] Policy violation NOT detected")
    scenarios_total += 1
    
    # Scenario 3: Denial of Service (Slowdown)
    print("\nScenario 3: DoS Attack (Response Time Degradation)")
    victim3 = "dos_agent"
    
    # Normal baseline
    for _ in range(15):
        rogue_detector.record_response_time(victim3, 0.5)
    
    # Attack: Suddenly slow (10s response)
    rogue_detector.record_response_time(victim3, 10.0)
    
    anomalies = rogue_detector.detect_anomaly(victim3)
    if 'timing_anomaly' in anomalies:
        level = agent_isolator.isolate(victim3, anomalies['timing_anomaly']['severity'], "DoS attack")
        if level != IsolationLevel.NONE:
            print(f" [PASS] DoS attack detected and isolated to {level.name}")
            scenarios_passed += 1
        else:
            print(f" [FAIL] No isolation applied")
    else:
        print(" [FAIL] DoS attack NOT detected")
    scenarios_total += 1
    
    # Scenario 4: Signature-Based Detection (Epic 13.4)
    print("\nScenario 4: Signature-Based Rogue Detection")
    victim4 = "signature_test_agent"
    
    # Create spam pattern
    for _ in range(15):
        rogue_detector.record_action_count(victim4, 2)
    rogue_detector.record_action_count(victim4, 100)
    
    # Check against known signatures
    signature_match = None
    for sig_name, sig_data in ROGUE_SIGNATURES.items():
        if sig_data["detector"](victim4):
            signature_match = sig_name
            break
    
    if signature_match:
        print(f" [PASS] Matched rogue signature: '{signature_match}'")
        scenarios_passed += 1
    else:
        print(" [FAIL] No signature match found")
    scenarios_total += 1
    
    # Summary
    print("\n" + "="*50)
    print(f"Red Team Results: {scenarios_passed}/{scenarios_total} scenarios detected")
    print(f"Detection Rate: {scenarios_passed/scenarios_total*100:.0f}%")
    
    if scenarios_passed == scenarios_total:
        print("SUCCESS: All rogue behaviors detected and isolated")
        return 0
    else:
        print("FAILURE: Some rogue behaviors evaded detection")
        return 1

if __name__ == "__main__":
    exit(run_rogue_red_team())
