from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from typing import List, Union, Optional
from models import Event, StatsResponse, PublishResponse
from aggregator import aggregator
from migration import init_db
import contextlib

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    await aggregator.start_worker()
    yield
    # Shutdown logic (if any)

app = FastAPI(
    title="Event Aggregator Service",
    description="A service to ingest, deduplicate, and process events.",
    version="1.0.0",
    lifespan=lifespan
)

@app.post("/publish", response_model=PublishResponse)
async def publish_events(events: Union[Event, List[Event]]):
    """
    Accept single or batch events.
    Validates schema strictly via Pydantic model.
    """
    try:
        count = await aggregator.enqueue_events(events)
        # Process all queued events immediately
        while not aggregator.queue.empty():
            event = await aggregator.queue.get()
            aggregator._persist_event(event)
            aggregator.queue.task_done()
        return PublishResponse(
            status="accepted",
            processed_count=count
        )

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/events")
async def get_events(topic: Optional[str] = Query(None)):
    """
    Returns list of unique processed events, optionally filtered by topic.
    """
    events = aggregator.get_events(topic)
    return events

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """
    Return system metrics.
    """
    return aggregator.get_stats()

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
