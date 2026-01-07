import logging
import math
import time
from typing import Dict, Tuple, Optional

logger = logging.getLogger("agent.behavioral_profiler")

class BehavioralProfiler:
    """
    Epic 9.3: Behavioral Profiling.
    Tracks user/agent behavior patterns to detect anomalies.
    MVP Feature: Impossible Travel (Geovelocity) detection.
    """
    
    def __init__(self):
        # Maps user_id -> (lat, lon, timestamp)
        self.last_known_location: Dict[str, Tuple[float, float, float]] = {}
        
        # Max reasonable travel speed (km/h) - e.g. Plane speed ~900km/h + buffer
        self.MAX_SPEED_KMH = 1200.0

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Haversine formula for distance between two points on Earth."""
        R = 6371.0 # Earth radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
             math.sin(dlon / 2) * math.sin(dlon / 2))
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        distance = R * c
        return distance

    def check_geovelocity(self, user_id: str, lat: float, lon: float) -> bool:
        """
        Checks if the movement from the last known location is physically possible.
        Returns True if SAFE, False if IMPOSSIBLE TRAVEL (Anomaly).
        """
        current_time = time.time()
        
        if user_id not in self.last_known_location:
            # First login: establish baseline
            self.last_known_location[user_id] = (lat, lon, current_time)
            return True
            
        last_lat, last_lon, last_time = self.last_known_location[user_id]
        
        # Calculate time delta (hours)
        time_diff_hours = (current_time - last_time) / 3600.0
        
        if time_diff_hours <= 0:
            # Simultaneous login from different location? Anomaly.
            if lat != last_lat or lon != last_lon:
                logger.warning(f"BEHAVIOR ALERT: Simultaneous login for {user_id} from different locations.")
                return False
            return True # Same location, same time (fast retry), ok.
            
        # Calculate distance (km)
        distance_km = self.calculate_distance(last_lat, last_lon, lat, lon)
        
        # Calculate speed (km/h)
        speed = distance_km / time_diff_hours
        
        if speed > self.MAX_SPEED_KMH:
            logger.warning(f"BEHAVIOR ALERT: Impossible Travel detected for {user_id}. Speed: {speed:.1f} km/h")
            return False
            
        # Update location
        self.last_known_location[user_id] = (lat, lon, current_time)
        return True

# Singleton
behavioral_profiler = BehavioralProfiler()
