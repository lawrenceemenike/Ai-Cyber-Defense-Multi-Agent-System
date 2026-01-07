import logging
import hashlib
import json
from typing import Dict
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import hashes, serialization

logger = logging.getLogger("agent.identity")

class AgentIdentityManager:
    """
    Epic 9.1: Agent Cryptographic Identities.
    Manages Public/Private key pairs for agents to prevent impersonation.
    """
    
    def __init__(self):
        # In a real system, private keys would be in a Hardware Security Module (HSM) or Vault across different pods.
        # For MVP, we simulate a centralized Key Management Service (KMS).
        self._private_keys: Dict[str, rsa.RSAPrivateKey] = {}
        self._public_keys: Dict[str, rsa.RSAPublicKey] = {}
        
        # Initialize standard agents
        self._generate_keypair("log_ingestion_agent")
        self._generate_keypair("threat_classification_agent")
        self._generate_keypair("mitigation_planning_agent")
        self._generate_keypair("action_execution_agent")
        self._generate_keypair("verifier_agent")
        self._generate_keypair("escalation_routing_agent")
        self._generate_keypair("audit_trail_agent")

    def _generate_keypair(self, agent_id: str):
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        self._private_keys[agent_id] = private_key
        self._public_keys[agent_id] = private_key.public_key()
        logger.info(f"Generated identity for '{agent_id}'")

    def sign_message(self, agent_id: str, message: str) -> bytes:
        """
        Signs a message using the agent's private key.
        """
        if agent_id not in self._private_keys:
            raise ValueError(f"Unknown agent: {agent_id}")
            
        private_key = self._private_keys[agent_id]
        signature = private_key.sign(
            message.encode('utf-8'),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return signature

    def verify_signature(self, agent_id: str, message: str, signature: bytes) -> bool:
        """
        Verifies a signature using the agent's public key.
        """
        if agent_id not in self._public_keys:
            logger.warning(f"Verification failed: Unknown agent '{agent_id}'")
            return False
            
        public_key = self._public_keys[agent_id]
        try:
            public_key.verify(
                signature,
                message.encode('utf-8'),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            logger.warning(f"Signature verification failed for '{agent_id}'")
            return False

# Singleton KMS
identity_manager = AgentIdentityManager()
