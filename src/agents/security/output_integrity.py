import logging
import hashlib
import json
from typing import Dict, Any, Tuple
from src.agents.security.agent_identity import identity_manager

logger = logging.getLogger("agent.output_integrity")

class OutputIntegrityChecker:
    """
    Epic 15.1: Agent Output Manipulation Detection.
    
    Ensures that agent outputs shown to humans haven't been tampered with
    between generation and display. Uses cryptographic signatures to verify integrity.
    """
    
    def sign_output(self, agent_id: str, output_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Signs an agent's output before it's sent to the human interface.
        
        Args:
            agent_id: Agent that generated the output
            output_data: The output payload
            
        Returns:
            Signed output package
        """
        # Create canonical representation
        serialized = json.dumps(output_data, sort_keys=True)
        
        # Generate signature
        signature = identity_manager.sign_message(agent_id, serialized)
        
        # Create signed package
        signed_output = {
            "agent_id": agent_id,
            "output": output_data,
            "signature": signature.hex(),
            "checksum": hashlib.sha256(serialized.encode()).hexdigest()
        }
        
        logger.debug(f"Output signed by '{agent_id}': {len(serialized)} bytes")
        return signed_output
    
    def verify_output(self, signed_output: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Verifies that output hasn't been tampered with.
        
        Args:
            signed_output: The signed output package
            
        Returns:
            (is_valid, error_message)
        """
        try:
            agent_id = signed_output["agent_id"]
            output_data = signed_output["output"]
            signature_hex = signed_output["signature"]
            claimed_checksum = signed_output["checksum"]
            
            # 1. Verify checksum (quick integrity check)
            serialized = json.dumps(output_data, sort_keys=True)
            actual_checksum = hashlib.sha256(serialized.encode()).hexdigest()
            
            if actual_checksum != claimed_checksum:
                logger.critical(
                    f"OUTPUT TAMPERING: Checksum mismatch for {agent_id}. "
                    f"Expected: {claimed_checksum[:16]}..., Got: {actual_checksum[:16]}..."
                )
                return False, "Checksum verification failed - output was modified"
            
            # 2. Verify cryptographic signature
            signature = bytes.fromhex(signature_hex)
            is_valid = identity_manager.verify_signature(agent_id, serialized, signature)
            
            if not is_valid:
                logger.critical(f"OUTPUT TAMPERING: Invalid signature from '{agent_id}'")
                return False, "Signature verification failed - output authenticity compromised"
            
            logger.debug(f"Output from '{agent_id}' verified successfully")
            return True, "OK"
            
        except (KeyError, ValueError) as e:
            logger.error(f"Malformed signed output: {e}")
            return False, f"Malformed output package: {e}"

# Singleton
output_integrity_checker = OutputIntegrityChecker()
