from pydantic import BaseModel
from datetime import datetime

class event(BaseModel):
    action: str
    timestamp: datetime
