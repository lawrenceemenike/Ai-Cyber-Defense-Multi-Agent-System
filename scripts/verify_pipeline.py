from src.graph.graph import app
import logging

logging.basicConfig(level=logging.INFO)

def test_pipeline():
    print("\n--- Starting Pipeline Integration Test ---\n")
    
    # 1. Simulate a Brute Force Log
    raw_log = {
        "source": "auth_server",
        "event_type": "login_failure", 
        "timestamp": "2024-01-01T12:00:00Z",
        "severity": "medium",
        "user": "admin",
        "source_ip": "192.168.100.45", # Sensitive subnet
        "raw_payload": {"error": "bad_password"}
    }
    
    initial_state = {
        "raw_log": raw_log,
        "normalized_log": None,
        "patterns_detected": [],
        "anomaly_score": 0.0,
        "threat_classification": None,
        "attack_path_hypothesis": None,
        "mitigation_plan": None,
        "verification_result": None,
        "escalation_decision": "hold",
        "human_feedback": None,
        "execution_result": None,
        "audit_record": None,
        "errors": []
    }
    
    result = app.invoke(initial_state)
    
    print("\n--- Test Results ---")
    print(f"1. Anomaly Score: {result.get('anomaly_score'):.2f} (Expected > 2.0 due to pattern+subnet)")
    print(f"2. Patterns: {[p['name'] for p in result.get('patterns_detected', [])]}")
    print(f"3. Classification: {result.get('threat_classification', {}).get('max_severity')}")
    print(f"4. Hypothesis: {result.get('attack_path_hypothesis')}")
    print(f"5. Plan Actions: {[a['name'] for a in result.get('mitigation_plan', {}).get('actions', [])]}")
    
    # Assertions
    assert result['anomaly_score'] > 0
    assert "Brute Force Attempt" in [p['name'] for p in result['patterns_detected']]
    assert result['mitigation_plan'] is not None

if __name__ == "__main__":
    test_pipeline()
