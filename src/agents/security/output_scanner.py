import logging
import re
import math
from typing import Tuple

logger = logging.getLogger("agent.output_scanner")

class OutputScanner:
    """
    Epic 7.4: Suspicious Output Pattern Monitoring.
    Scans agent output for patterns indicating data exfiltration or obfuscation.
    Targeting: Base64 blobs, Hex dumps, Hidden URLs.
    """
    
    def __init__(self):
        # Regex for potential Base64 strings (long sequences of alphanumeric + padding)
        # We look for continuous chunks > 40 chars to avoid false positives on simple IDs.
        self.base64_pattern = re.compile(r'(?:[A-Za-z0-9+/]{40,})(?:={0,2})')
        
        # Regex for IPs and URLs that shouldn't be in the output (if we enforce a strict policy)
        self.url_pattern = re.compile(r'https?://[^\s]+')
        
    def scan(self, text: str) -> Tuple[bool, str]:
        """
        Scans text for suspicious patterns.
        Returns (IsSafe, WarningMessage).
        """
        if not text:
            return True, "Empty"

        # 1. Base64 / High Entropy Blob Detection
        blobs = self.base64_pattern.findall(text)
        if blobs:
            logger.warning(f"SUSPICIOUS OUTPUT: Potential Base64 blob detected (Len: {len(blobs[0])})")
            return False, "Potential Data Exfiltration (Base64 Blob)"
            
        # 2. Shannon Entropy Check (General Obfuscation)
        # A normal English sentence has entropy around 3.5-4.5. Encrypted/Compressed data is > 5.5.
        if self._calculate_entropy(text) > 5.8 and len(text) > 100:
             logger.warning(f"SUSPICIOUS OUTPUT: Abnormally high entropy ({self._calculate_entropy(text):.2f})")
             return False, "High Entropy detected (Potential Encrypted/Obfuscated Data)"

        # 3. URL Exfiltration Check (Simulated policy: No external links)
        # In a real secure env, we might ban all URLs.
        if self.url_pattern.search(text):
            # We allow internal localhost links, block external
            if "localhost" not in text and "127.0.0.1" not in text:
                 logger.warning("SUSPICIOUS OUTPUT: External URL detected.")
                 return False, "External URL Exfiltration Risk"

        return True, "Safe"

    def _calculate_entropy(self, text: str) -> float:
        """Calculates Shannon Entropy of the string."""
        prob = [float(text.count(c)) / len(text) for c in dict.fromkeys(list(text))]
        entropy = - sum([p * math.log(p) / math.log(2.0) for p in prob])
        return entropy

# Singleton
output_scanner = OutputScanner()
