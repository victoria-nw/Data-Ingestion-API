from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional



class event(BaseModel):
    event_type: str = Field(..., description="Type of event")
    event_id: str = Field(..., description="ID of related entity")
    payload: dict 
    occurred_at: datetime
    user_id: Optional[str] = None
