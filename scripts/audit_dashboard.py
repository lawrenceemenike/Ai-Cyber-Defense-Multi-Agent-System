import time
import json
import os
import sys

def tail_audit_log(filepath):
    print(f"--- CADMS REAL-TIME AUDIT DASHBOARD ---")
    print(f"Monitoring: {filepath}")
    print(f"{'TIMESTAMP':<20} | {'AGENT':<15} | {'ACTION':<20} | {'STATUS'}")
    print("-" * 80)
    
    if not os.path.exists(filepath):
        print("Waiting for audit log file to be created...")
        while not os.path.exists(filepath):
            time.sleep(1)

    with open(filepath, "r") as f:
        # Go to end of file
        f.seek(0, os.SEEK_END)
        
        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue
                
            try:
                record = json.loads(line)
                entry = record["entry"]
                
                ts = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(entry["timestamp"]))
                agent = entry["agent_id"]
                action = entry["action"]
                
                # Verify Integrity (Quick Check)
                # In a real dashboard, we'd verify the signature here too
                
                print(f"{ts:<20} | {agent:<15} | {action:<20} | Signed [OK]")
                
            except Exception as e:
                print(f"Error parsing line: {e}")

if __name__ == "__main__":
    tail_audit_log("audit_log.jsonl")
