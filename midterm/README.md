# Event Aggregator Service

A robust, self-contained event aggregation service built with Python, FastAPI, and SQLite. This service ingests events, deduplicates them based on `(topic, event_id)`, and persists unique events for querying.

## 🚀 Key Features

- **High-Throughput Ingestion**: Batch and single event support with asynchronous background processing.
- **Persistent Deduplication**: Guaranteed idempotency using SQLite with indexed composite keys.
- **Observability**: Real-time statistics and event retrieval endpoints.
- **Reliable**: Crash-tolerant design ensures no duplicate processing after restarts.
- **Dockerized**: Easy deployment with `uv` package manager and multi-service orchestration.

---

## 🛠 Setup & Run

### Prerequisites
- Docker & Docker Compose

### Fast Start (Docker Compose)
To start the entire system (Aggregator + Publisher Simulation):
```bash
docker compose up --build
```
The **Aggregator** will be available at `http://localhost:8080`.
The **Publisher** will automatically start sending 5,000 events (including ~20% duplicates).

### Manual Run (Local)
If you have `uv` and Python 3.11+ installed:
```bash
# Install dependencies
uv sync

# Run the server
uv run uvicorn main:app --host 0.0.0.0 --port 8080
```

---

## 📖 API Usage Examples

### 1. Publish Events
**POST** `/publish`
```json
[
  {
    "topic": "orders",
    "event_id": "ORD-123",
    "timestamp": "2024-03-20T10:00:00Z",
    "source": "checkout-service",
    "payload": {"amount": 99.99, "currency": "USD"}
  }
]
```

### 2. Get Statistics
**GET** `/stats`
```json
{
  "received": 5000,
  "unique_processed": 4012,
  "duplicate_dropped": 988,
  "topics": ["orders", "inventory", "notifications"],
  "uptime": 120.5
}
```

### 3. Retrieve Events
**GET** `/events?topic=orders`
Returns a list of unique processed events for the specified topic.

---

## 🧪 Running Tests
The test suite covers deduplication, persistence, and schema validation.
```bash
# Run tests inside docker
docker compose run --rm aggregator pytest
```

---

## 📝 Design Decisions & Assumptions

### 1. Ordering
**Decision**: The system maintains **internal FIFO ordering** via an `asyncio.Queue` and a single-threaded background worker.
**Justification**: While total global ordering across all possible distributed producers cannot be guaranteed by the aggregator alone (due to network latency), the service ensures that once an event is received, it is processed in the order of arrival. This satisfies the requirements without the overhead of complex sequencing protocols.

### 2. Performance
The use of an internal queue prevents the `/publish` API from blocking during database writes. This allows the system to handle high ingestion spikes while the background worker catches up with persistence and deduplication.

### 3. Persistent Store
**SQLite** was chosen for its zero-configuration requirement and ACID compliance. Composite indexes on `(topic, event_id)` allow for extremely fast deduplication lookups at scale.

### 4. Idempotency
At-least-once delivery semantics are handled by the deduplication layer. If a publisher retries a request, the service will accept it (200 OK) but transparently drop the duplicate in the background, ensuring data integrity.
