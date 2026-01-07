from pydantic import BaseModel, Field
from typing import Optional

class NormalizedLog(BaseModel):
    """
    Standardized schema for all ingested logs.
    """
    event_id: str
    timestamp: str
    source: str
    event_type: str
    severity: str
    user: Optional[str] = None
    source_ip: Optional[str] = None
    action: Optional[str] = None
    raw_payload: str # Stored as stringified JSON to be generic
