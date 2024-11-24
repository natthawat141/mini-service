from pydantic import BaseModel
from datetime import datetime

class RecommendationResponse(BaseModel):
    recommendation: str            # คำแนะนำจาก AI
    timestamp: datetime