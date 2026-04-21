from sqlalchemy import create_engine, Column, String, DateTime, JSON, UniqueConstraint, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////database/events.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class ProcessedEvent(Base):
    __tablename__ = "processed_events"

    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String, index=True)
    event_id = Column(String, index=True)
    timestamp = Column(DateTime)
    source = Column(String)
    payload = Column(JSON)

    # Composite unique constraint for deduplication
    __table_args__ = (UniqueConstraint('topic', 'event_id', name='_topic_event_id_uc'),)

def init_db():
    print(engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
