import logging
import time
from typing import Dict, List, Set
from src.agents.security.message_integrity import message_integrity

logger = logging.getLogger("agent.consensus")

class ConsensusManager:
    """
    Epic 12.2: Multi-Agent Consensus & 12.4: Anti-Replay (Nonces).
    
    For critical decisions, requires agreement from multiple agents.
    Also prevents replay attacks using nonces.
    """
    
    def __init__(self):
        # Track used nonces to prevent replay
        self.used_nonces: Set[str] = set()
        
        # Consensus threshold (e.g., 2 out of 3 agents must agree)
        self.consensus_threshold = 0.66  # 66%
    
    def generate_nonce(self) -> str:
        """Generates a unique nonce for message freshness."""
        import uuid
        return f"nonce_{uuid.uuid4().hex}"
    
    def check_nonce(self, nonce: str) -> bool:
        """
        Checks if nonce has been used before (Epic 12.4: Anti-Replay).
        Returns True if fresh, False if replay.
        """
        if nonce in self.used_nonces:
            logger.warning(f"REPLAY ATTACK: Nonce '{nonce}' already used")
            return False
        
        self.used_nonces.add(nonce)
        return True
    
    def collect_votes(self, decision: Dict, voting_agents: List[str]) -> bool:
        """
        Epic 12.2: Collects signed votes from multiple agents.
        
        Args:
            decision: The decision to vote on
            voting_agents: List of agent IDs that should vote
            
        Returns:
            True if consensus reached, False otherwise
        """
        # In a real implementation, this would:
        # 1. Broadcast decision to all voting agents
        # 2. Wait for signed responses
        # 3. Verify signatures
        # 4. Count votes
        
        # For MVP, we simulate the voting process
        votes = {}
        
        for agent in voting_agents:
            # Simulate agent voting (in reality, would be async message passing)
            # Here we just create a signed vote
            vote_data = {
                "decision_id": decision.get("id", "unknown"),
                "vote": "approve",  # Simplified: in reality would have logic
                "nonce": self.generate_nonce()
            }
            
            signed_vote = message_integrity.sign_message(agent, vote_data)
            
            # Verify the vote
            if message_integrity.verify_message(signed_vote, expected_sender=agent):
                nonce = message_integrity.extract_payload(signed_vote)["nonce"]
                if self.check_nonce(nonce):
                    votes[agent] = message_integrity.extract_payload(signed_vote)["vote"]
                else:
                    logger.warning(f"Rejected replay vote from '{agent}'")
            else:
                logger.warning(f"Invalid vote signature from '{agent}'")
        
        # Calculate consensus
        approve_count = sum(1 for v in votes.values() if v == "approve")
        consensus_ratio = approve_count / len(voting_agents) if voting_agents else 0
        
        if consensus_ratio >= self.consensus_threshold:
            logger.info(f"Consensus REACHED: {approve_count}/{len(voting_agents)} agents approved")
            return True
        else:
            logger.warning(f"Consensus FAILED: Only {approve_count}/{len(voting_agents)} approved (need {self.consensus_threshold*100}%)")
            return False

# Singleton
consensus_manager = ConsensusManager()
