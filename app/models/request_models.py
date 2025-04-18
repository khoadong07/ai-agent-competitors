from pydantic import BaseModel, Field
from typing import List

class InsightRequest(BaseModel):
    topic_ids: List[str] = Field(..., min_items=1, description="List of topic IDs")
    from_date1: str = Field(..., description="Start date for period 1 in 'YYYY-MM-DDTHH:MM' format")
    to_date1: str = Field(..., description="End date for period 1 in 'YYYY-MM-DDTHH:MM' format")
    from_date2: str = Field(..., description="Start date for period 2 in 'YYYY-MM-DDTHH:MM' format")
    to_date2: str = Field(..., description="End date for period 2 in 'YYYY-MM-DDTHH:MM' format")