# 🛰 Visual Order Processing System (gRPC + Kafka)

This system demonstrates the difference between **Synchronous (gRPC)** and **Asynchronous (Pub/Sub)** communication in a distributed environment.

## 🏗 Architecture

1.  **Frontend (Nginx/Alpine.js)**: A dashboard that visualizes the flow of requests and events.
2.  **Order Service (Java/Spring Boot)**: Acts as the entry point. Receives gRPC requests, validates them, and produces Kafka events.
3.  **Kafka (Message Broker)**: Decouples the order creation from downstream processing.
4.  **Inventory Service**: Consumes events to update stock.
5.  **Notification Service**: Consumes events to send simulated emails (includes retry logic).
6.  **Analytics Service**: Consumes events to aggregate system-wide stats.

## 🚀 How to Run

Ensure you have **Docker** and **Docker Compose** installed.

```bash
docker-compose up --build
```

Access the dashboard at: [http://localhost:3000](http://localhost:3000)

## 🧪 Scenarios to Try

1.  **Normal Flow**: Enter a User ID and Item. Click "Place Order". Observe how the gRPC response is nearly instant (Timeline), while the subscriber updates follow shortly after via the Event Stream.
2.  **Failure Demo**: Set quantity to **> 100**. The Order Service will return a `FAILED` status via gRPC. No Kafka event will be published, and subscribers will not react.
3.  **Resilience Demo**: Notification service has a 20% simulated failure rate. Watch the notification log to see retries in action.

## 🛠 Tech Stack
- **Backend**: Java 21, Spring Boot 3.4, Spring Kafka, gRPC (net.devh)
- **Frontend**: Alpine.js, CSS Grid/Flexbox, HTML5 WebSockets
- **Ops**: Docker, Bitnami Kafka (KRaft mode)
