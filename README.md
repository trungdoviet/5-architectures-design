# Microservices Design Patterns

A comprehensive collection of **9 essential microservices design patterns** — each with detailed documentation, architecture diagrams, and working demo projects in **Java** and **Python**.

---

## 📚 Patterns

### 1. [Strangler Fig Pattern](./01-strangler-fig-pattern/README.md)

Facilitates the **gradual replacement** of a monolithic system with microservices, ensuring a smooth and risk-free transition. A facade routes traffic between legacy and new services, enabling zero-downtime migration with instant rollback capability.

> **Demo:** E-Commerce order processing — migrating from a monolith to microservices

---

### 2. [API Gateway Pattern](./02-api-gateway-pattern/README.md)

Centralizes external access to your microservices, providing a **single entry point** for all client requests. Handles cross-cutting concerns like authentication, rate limiting, request aggregation, and centralized logging.

> **Demo:** Social Network platform — unified gateway for user, post, and notification services

---

### 3. [Backends for Frontends (BFF) Pattern](./03-backends-for-frontends-pattern/README.md)

Creates **dedicated backend services for each frontend** type (web, mobile, IoT), optimizing performance and user experience tailored to each platform. Each BFF shapes API responses specifically for its client's needs.

> **Demo:** Banking application — rich web dashboard vs. compact mobile app responses

---

### 4. [Service Discovery Pattern](./04-service-discovery-pattern/README.md)

Enables microservices to **dynamically discover and communicate** with each other without hardcoded URLs. Services self-register, send heartbeats, and are automatically removed when they go down — simplifying orchestration and enhancing scalability.

> **Demo:** Logistics system — dynamic discovery of fleet, warehouse, and routing services

---

### 5. [Circuit Breaker Pattern](./05-circuit-breaker-pattern/README.md)

Implements a **fault-tolerant mechanism** that prevents cascading failures by automatically detecting and isolating faulty services. Uses a three-state model (CLOSED → OPEN → HALF-OPEN) with fallback responses and self-healing recovery.

> **Demo:** Medical appointment system — protecting booking service from payment service failures

---

### 6. [Saga Pattern](./06-saga-pattern/README.md)

Manages **distributed transactions** and maintains consistency across multiple microservices without using global ACID transactions. Breaks complex flows into a sequence of local transactions, employing compensating transactions (rollbacks) when failures occur.

> **Demo:** E-Commerce order processing — coordinating order creation, payment processing, and inventory reservation

---

### 7. [CQRS Pattern](./07-cqrs-pattern/README.md)

Stands for **Command Query Responsibility Segregation**. Separates data mutation operations (Commands) from data retrieval operations (Queries) into completely distinct models, maximizing optimization and scaling for read-heavy applications.

> **Demo:** Optimized user repository with separate Write (entity) and Read (flat view) services

---

### 8. [Event Sourcing Pattern](./08-event-sourcing-pattern/README.md)

Replaces traditional CRUD database updates by storing the state of the system as an **append-only sequence of immutable events**. Current state is established by replaying the event log from the beginning.

> **Demo:** Shopping Cart entity rebuilding its inventory purely by replaying historical events

---

### 9. [Sidecar Pattern](./09-sidecar-pattern/README.md)

Attaches a secondary container/process (the sidecar) to a primary microservice to handle **cross-cutting concerns** like logging, proxying, monitoring, or networking without mutating the primary application's codebase.

> **Demo:** A logging/tracing Sidecar intercepting and formatting output from a naive legacy application

---

## 🛠️ How to Use

Each pattern folder contains:

| File | Description |
|------|-------------|
| `README.md` | What, When, Why, How + Architecture diagrams + Implementation guide |
| `demo/java/` | Self-contained Java demo (compile with `javac`, run with `java`) |
| `demo/python/` | Multi-service Flask demo with real HTTP communication |

### Quick Start — Java

```bash
cd <pattern-folder>/demo/java
javac -d out *.java
java -cp out <MainClass>
```

### Quick Start — Python

```bash
cd <pattern-folder>/demo/python
pip install flask requests
# Start each service in a separate terminal, then run test_client.py
python test_client.py
```
