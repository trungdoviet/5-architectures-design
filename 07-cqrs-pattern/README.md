# CQRS Pattern (Command Query Responsibility Segregation)

## 1. Overview — What Is It?

CQRS stands for **Command Query Responsibility Segregation**. At its heart, it states that the operations that mutate data (Commands) should be strictly separated from the operations that read data (Queries).

In a traditional CRUD system, the same data model is used for inserting, updating, and querying. As systems grow complex, reading data often requires complex JOINs or aggregations, while writing data requires strict validation. CQRS solves this by splitting the conceptual model into two distinct pieces:
1. **Write Model (Commands)**: Handles updates, complex business logic, validation, and domain rules.
2. **Read Model (Queries)**: Highly optimized for querying. Often denormalized (e.g., a flat table or NoSQL document) so UI components can fetch data instantly without complex table joins.

## 2. When to Use

| Scenario | Applicability |
|----------|--------------|
| High read-to-write ratio (system is queried frequently but updated rarely) | ✅ Ideal |
| Complex UI requiring data aggregated from multiple sources | ✅ Ideal |
| Microservices requiring event-driven architectures | ✅ Ideal |
| Simple CRUD applications where reads & writes are identical | ❌ Overkill |

## 3. Why to Use — Benefits & Trade-offs

### ✅ Benefits
* **Independent Scaling**: Scale the Read APIs differently from the Write APIs.
* **Optimized Data Retrieval**: Read models can be completely denormalized.
* **Separation of Concerns**: Prevents complex validation logic from tangling with query logic.

### ⚠️ Trade-offs
* **Eventual Consistency**: Because Read models must be populated/synced from Write models, there might be a slight delay. The UI must be able to handle this.
* **Complexity**: You now maintain two distinct models and potentially two distinct databases.

## 4. Architecture Design

```mermaid
graph TB
    Client[Client / UI]
    CommandService[Command API]
    QueryService[Query API]
    WriteDB[(Write Database)]
    ReadDB[(Read Database)]
    EventBus[Event Bus / Message Broker]
    
    Client -->|1. Submit Command (Create/Update)| CommandService
    CommandService -->|2. Validate & Save| WriteDB
    CommandService -->|3. Publish Event| EventBus
    EventBus -->|4. Sync / Update| QueryService
    QueryService -->|5. Save Denormalized Data| ReadDB
    
    Client -->|Fetch Data| QueryService
    QueryService -->|Return Fast Result| Client

    style CommandService fill:#e74c3c,color:#fff
    style QueryService fill:#27ae60,color:#fff
    style WriteDB fill:#c0392b,color:#fff
    style ReadDB fill:#2ecc71,color:#fff
    style EventBus fill:#f39c12,color:#fff
```

## 5. Demo Structure

In this demo, we simulate a **User Repository**:
1. **Command Side**: Handles `createUser` and `updateUserEmail`. It applies business rules and then pushes an event to a local queue.
2. **Event Handler / Sync**: Consumes the event and updates the **Read Side** (a denormalized projection).
3. **Query Side**: Easily fetches the user's display information.

### How to Run

#### Python Demo
```bash
cd demo/python
python test_cqrs.py
```

#### Java Demo
```bash
cd demo/java
javac -d out src/*.java
java -cp out CQRSDemo
```

## 6. Key Takeaway
> **Separate reads from writes to scale independently.** CQRS splits your application into two distinct models—a Write model focusing on validation and business logic, and a Read model purely optimized for fast data retrieval.

## 7. Knowledge Quiz

<details>
<summary><strong>Question 1: What does "Command" and "Query" refer to in CQRS?</strong></summary>
A Command mutates the state of the system (Create, Update, Delete). A Query returns the state (Read) without altering it.
</details>

<details>
<summary><strong>Question 2: Does CQRS require two separate databases?</strong></summary>
No. You can implement CQRS at the application level using a single database. However, using separate databases (e.g., SQL for writes, NoSQL/Redis for reads) is a very common macro-architecture pattern.
</details>

<details>
<summary><strong>Question 3: What is the main trade-off of maintaining a separate Write and Read database?</strong></summary>
Eventual Consistency. Syncing data from the Write DB to the Read DB happens asynchronously, meaning a user might very briefly query stale data immediately after a write.
</details>
