from pydantic import BaseModel
from typing import Optional

class SOVInsightResponse(BaseModel):
    report: Optional[str]