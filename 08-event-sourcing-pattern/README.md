# Event Sourcing Pattern

## 1. Overview — What Is It?

The **Event Sourcing Pattern** is an architectural approach where the state of a system is not stored as a current "snapshot" (like a traditional database table row). Instead, the system stores **every single state-mutating event** that has ever happened in an append-only log (an Event Store).

To determine the current state of an entity (e.g., a Bank Account), the system "replays" all the events from the beginning of time.

### Traditional vs Event Sourcing

* **Traditional (CRUD)**: `UPDATE BankAccount SET balance = 50 WHERE id = 1` -> The previous balance history is overwritten and lost forever.
* **Event Sourcing**:
    1. `AccountCreatedEvent(id=1, initial_balance=0)`
    2. `MoneyDepositedEvent(id=1, amount=100)`
    3. `MoneyWithdrawnEvent(id=1, amount=50)`
    *Current Balance* is dynamically calculated as: $0 + $100 - $50 = $50.

## 2. When to Use

| Scenario | Applicability |
|----------|--------------|
| Systems requiring strict audit trails (e.g., Banking, Accounting) | ✅ Ideal |
| Building temporal applications (navigating state at any point in time) | ✅ Ideal |
| Highly concurrent systems where database locks perform poorly | ✅ Ideal |
| Simple applications with straightforward CRUD data | ❌ Overkill |

## 3. Why to Use — Benefits & Trade-offs

### ✅ Benefits
* **Infallible Audit Trail**: You have a 100% accurate history of everything that ever happened. You don't just know *what* the state is, you know *how* it got there.
* **Time Travel**: You can recreate the system state at any exact second in the past.
* **Append-Only Performance**: Appending events to a log is incredibly fast, avoiding complex locks and updates blockages.

### ⚠️ Trade-offs
* **Replay Performance**: Rebuilding state from thousands of events takes time. (Solved via snapshotting).
* **Steep Learning Curve**: Changing from a relational model to an event-based model requires a massive paradigm shift.
* **Event Migration**: What happens when the schema of an event changes 2 years into production? You must handle versioning of events carefully.

## 4. Architecture Design

```mermaid
graph TB
    Client[Client / UI]
    CommandAPI[Command Handler]
    EventStore[(Append-Only Event Store)]
    Projector[Projection Engine (Read Model)]
    ReadDB[(Read Database)]
    
    Client -->|1. Submit Action (Deposit)| CommandAPI
    CommandAPI -->|2. Append 'MoneyDeposited'| EventStore
    EventStore -.->|3. Publish Event| Projector
    Projector -->|4. Update Snapshot/View| ReadDB
    Client -->|Fetch Balance| ReadDB

    style EventStore fill:#f39c12,color:#fff
    style ReadDB fill:#2ecc71,color:#fff
```

*(Note: Event Sourcing is almost always paired with the CQRS pattern to build reliable Read Models because querying an append-only log directly is highly inefficient).*

## 5. Demo Structure

In this demo, we simulate a **Shopping Cart**:
1. We have an **Event Store** containing our append-only log.
2. We create events: `CartCreated`, `ItemAdded`, `ItemRemoved`.
3. We have a **Cart Entity** that doesn't save to a database. It simply reconstructs its state by replaying events from the store.

### How to Run

#### Python Demo
```bash
cd demo/python
python test_event_sourcing.py
```

#### Java Demo
```bash
cd demo/java
javac -d out src/*.java
java -cp out EventSourcingDemo
```

## 6. Key Takeaway
> **Store the facts, derive the state.** Instead of storing the current state of an entity, Event Sourcing strictly stores the sequence of events that occurred. The current state is just a projection calculated by replaying those events.

## 7. Knowledge Quiz

<details>
<summary><strong>Question 1: What is the main structural characteristic of an Event Store?</strong></summary>
It is exclusively append-only. Events are never updated or deleted; if a mistake was made, a new compensating event is appended.
</details>

<details>
<summary><strong>Question 2: How do you solve the performance issue of replaying 10,000 events just to get the current state?</strong></summary>
By using "Snapshots". The system periodically calculates and saves the state (e.g., every 100 events). To get current state, it loads the most recent snapshot and only replays the events that happened after it.
</details>

<details>
<summary><strong>Question 3: Why are Event Sourcing and CQRS almost always paired together?</strong></summary>
Because querying an Event Store is terrible for UI performance (you can't easily do a "Give me all users older than 20" SQL query on an event log). CQRS allows you to project those events into a standard Read Database optimized for those queries.
</details>
