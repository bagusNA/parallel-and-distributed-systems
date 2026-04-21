import asyncio
import time
import logging
from typing import List, Dict, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from .models import Event
from .database import ProcessedEvent, SessionLocal, init_db

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class EventAggregator:
    def __init__(self):
        self.queue = asyncio.Queue()
        self.start_time = time.time()
        self.received_count = 0
        self.unique_processed_count = 0
        self.duplicate_dropped_count = 0
        self.worker_task = None
        self._initialize_stats()

    def _initialize_stats(self):
        """Load initial stats from database on startup."""
        db = SessionLocal()
        try:
            init_db()

            self.unique_processed_count = db.query(ProcessedEvent).count()
            logger.info(f"Initialized aggregator with {self.unique_processed_count} existing events.")
        finally:
            db.close()

    async def enqueue_events(self, events: Union[Event, List[Event]]):
        if isinstance(events, Event):
            events = [events]
        
        for event in events:
            self.received_count += 1
            await self.queue.put(event)
        
        return len(events)

    async def start_worker(self):
        logger.info("Starting background worker...")
        self.worker_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        while True:
            event = await self.queue.get()
            try:
                self._persist_event(event)
            except Exception as e:
                logger.error(f"Error processing event {event.event_id}: {str(e)}")
            finally:
                self.queue.task_done()

    def _persist_event(self, event: Event):
        db = SessionLocal()
        try:
            new_event = ProcessedEvent(
                topic=event.topic,
                event_id=event.event_id,
                timestamp=event.timestamp,
                source=event.source,
                payload=event.payload
            )
            db.add(new_event)
            db.commit()
            self.unique_processed_count += 1
            logger.info(f"Processed unique event: {event.topic}/{event.event_id}")
        except IntegrityError:
            db.rollback()
            self.duplicate_dropped_count += 1
            logger.info(f"Dropped duplicate event: {event.topic}/{event.event_id}")
        finally:
            db.close()

    def get_stats(self):
        db = SessionLocal()
        try:
            topics = [r[0] for r in db.query(ProcessedEvent.topic).distinct().all()]
        finally:
            db.close()
            
        return {
            "received": self.received_count,
            "unique_processed": self.unique_processed_count,
            "duplicate_dropped": self.duplicate_dropped_count,
            "topics": topics,
            "uptime": time.time() - self.start_time
        }

    def get_events(self, topic: str = None):
        db = SessionLocal()
        try:
            query = db.query(ProcessedEvent)
            if topic:
                query = query.filter(ProcessedEvent.topic == topic)
            events = query.all()
            return [
                {
                    "topic": e.topic,
                    "event_id": e.event_id,
                    "timestamp": e.timestamp.isoformat(),
                    "source": e.source,
                    "payload": e.payload
                } for e in events
            ]
        finally:
            db.close()

# Singleton instance
aggregator = EventAggregator()
