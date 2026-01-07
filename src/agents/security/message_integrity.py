import logging
import json
import time
from typing import Dict, Any
from src.agents.security.agent_identity import identity_manager

logger = logging.getLogger("agent.message_integrity")

class MessageIntegrityManager:
    """
    Epic 12.1: Signed Inter-Agent Messages.
    Ensures messages passed between agents are cryptographically signed.
    """
    
    def sign_message(self, sender_agent: str, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Signs a message from an agent before passing it to another agent.
        
        Returns:
            Signed message with metadata
        """
        # Create envelope
        envelope = {
            "sender": sender_agent,
            "timestamp": time.time(),
            "payload": message_data
        }
        
        # Serialize and sign
        serialized = json.dumps(envelope, sort_keys=True)
        signature = identity_manager.sign_message(sender_agent, serialized)
        
        # Return signed envelope
        signed_message = {
            "envelope": envelope,
            "signature": signature.hex()  # Convert bytes to hex string for JSON compatibility
        }
        
        logger.debug(f"Message signed by '{sender_agent}'")
        return signed_message
    
    def verify_message(self, signed_message: Dict[str, Any], expected_sender: str = None) -> bool:
        """
        Verifies the signature of a received message.
        
        Args:
            signed_message: The signed message envelope
            expected_sender: Optional - verify sender identity
            
        Returns:
            True if valid, False if tampered/invalid
        """
        try:
            envelope = signed_message["envelope"]
            signature_hex = signed_message["signature"]
            signature = bytes.fromhex(signature_hex)
            
            sender = envelope["sender"]
            
            # Optional: Verify expected sender
            if expected_sender and sender != expected_sender:
                logger.warning(f"Sender mismatch: expected '{expected_sender}', got '{sender}'")
                return False
            
            # Verify signature
            serialized = json.dumps(envelope, sort_keys=True)
            is_valid = identity_manager.verify_signature(sender, serialized, signature)
            
            if not is_valid:
                logger.critical(f"INTEGRITY VIOLATION: Invalid signature from '{sender}'")
                return False
                
            logger.debug(f"Message from '{sender}' verified successfully")
            return True
            
        except (KeyError, ValueError) as e:
            logger.error(f"Malformed message: {e}")
            return False
    
    def extract_payload(self, signed_message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts the payload from a verified message.
        Should only be called after verify_message returns True.
        """
        return signed_message["envelope"]["payload"]

# Singleton
message_integrity = MessageIntegrityManager()
