from src.agents.security.behavioral_profiler import behavioral_profiler
import logging
import time

logging.basicConfig(level=logging.ERROR)

def test_behavioral_profiling():
    print("\n--- Starting Behavioral Profiling Test ---\n")
    
    user = "analyst_01"
    
    # 1. First Login (New York)
    print("Test 1: Initial Login (New York)")
    # NY Coordinates: 40.7128, -74.0060
    if behavioral_profiler.check_geovelocity(user, 40.7128, -74.0060):
        print(" [PASS] Baseline established.")
    else:
        print(" [FAIL] Baseline rejected.")
        raise AssertionError("Baseline failed")

    # 2. Feasible Travel (Philadelphia, 2 hours later)
    print("\nTest 2: Feasible Travel (Philly, simulated 2 hours later)")
    # Resetting internal state specifically for this test or mocking time would be cleaner,
    # but for this script we will manually update the 'last_known' timestamp to be in the past.
    
    # Mocking past time: Set the NY login to 2 hours ago
    last_lat, last_lon, _ = behavioral_profiler.last_known_location[user]
    behavioral_profiler.last_known_location[user] = (last_lat, last_lon, time.time() - 7200) # 2 hours ago
    
    # Philly: 39.9526, -75.1652 (approx 130km away)
    if behavioral_profiler.check_geovelocity(user, 39.9526, -75.1652):
        print(" [PASS] Feasible travel accepted.")
    else:
        print(" [FAIL] Feasible travel blocked.")
        raise AssertionError("Feasible travel failed")

    # 3. Impossible Travel (London, 5 mins later)
    print("\nTest 3: Impossible Travel (London, 5 mins later)")
    # London: 51.5074, -0.1278 (Thousands of km away)
    # Distance from Philly ~5700km. Time diff ~5 mins (mocked).
    
    # Set Philly login to 5 mins ago
    last_lat, last_lon, _ = behavioral_profiler.last_known_location[user]
    behavioral_profiler.last_known_location[user] = (last_lat, last_lon, time.time() - 300) 
    
    if not behavioral_profiler.check_geovelocity(user, 51.5074, -0.1278):
        print(" [PASS] Impossible travel correctly flagged.")
    else:
        print(" [FAIL] Impossible travel ALLOWED.")
        raise AssertionError("Impossible travel check failed")

if __name__ == "__main__":
    test_behavioral_profiling()
