from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Any, Dict, List, Optional

class Event(BaseModel):
    topic: str = Field(..., description="The topic of the event")
    event_id: str = Field(..., description="Unique ID per topic")
    timestamp: datetime = Field(..., description="ISO8601 string")
    source: str = Field(..., description="Source of the event")
    payload: Dict[str, Any] = Field(..., description="Arbitrary JSON payload")

    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "topic": "sensor_reading",
                "event_id": "evt_123",
                "timestamp": "2024-03-20T10:00:00Z",
                "source": "iot_node_01",
                "payload": {"temperature": 22.5, "humidity": 65}
            }
        }
    )

class StatsResponse(BaseModel):
    received: int
    unique_processed: int
    duplicate_dropped: int
    topics: List[str]
    uptime: float  # seconds

class PublishResponse(BaseModel):
    status: str
    processed_count: int
    invalid_events: Optional[List[Dict[str, Any]]] = None
