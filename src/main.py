from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional
import uvicorn
import logging
from src.graph.graph import app as graph_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cadms-api")

app = FastAPI(
    title="CADMS API",
    description="AI Cyber-Defense Multi-Agent System API",
    version="0.1.0"
)

# --- Input Models ---
class LogEvent(BaseModel):
    source: str
    event_type: str
    timestamp: str
    raw_payload: Dict[str, Any]

class ThreatResponse(BaseModel):
    threat_id: str
    status: str
    mitigation_plan: Optional[Dict[str, Any]] = None

# --- Endpoints ---

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "cadms-core"}

from src.agents.utility.resource_manager import resource_manager
import uuid

# ...

@app.post("/ingest", response_model=ThreatResponse)
async def ingest_log(event: LogEvent):
    """
    Ingest a new log event and trigger the agent pipeline.
    """
    req_id = str(uuid.uuid4())
    logger.info(f"Received event from {event.source} (Req: {req_id})")
    
    # Epic 4: Start Resource Tracking
    resource_manager.start_request(req_id)
    
    # Initialize state
    initial_state = {
        "raw_log": event.model_dump(),
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
        "errors": [],
        "request_id": req_id # Pass ID down for agents to report usage
    }

    try:
        # Run graph
        # Note: In a real implementation, we'd pass resource_manager into the graph context 
        # or have agents import the singleton and report usage using state['request_id'].
        final_state = graph_app.invoke(initial_state)
        
        # Epic 4: Final Resource Check
        if not resource_manager.check_timeout(req_id):
             raise HTTPException(status_code=408, detail="Request Timeout")
             
        stats = resource_manager.get_stats(req_id)
        logger.info(f"Request {req_id} completed. Stats: {stats}")
        
        return {
            "threat_id": req_id,
            "status": "processed",
            "mitigation_plan": final_state.get("mitigation_plan")
        }
        
    except Exception as e:
        logger.error(f"Pipeline error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
