from typing import Optional
from pydantic import BaseModel, conint


class Score(BaseModel):
    event_id: int
    score: conint(ge=0, le=5)


class RabbitMQEvent(BaseModel):
    data: Optional[dict]
    event: str
    status: str
