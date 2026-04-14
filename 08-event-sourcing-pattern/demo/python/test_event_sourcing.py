import time

class DomainEvent:
    def __init__(self, entity_id, event_type, payload):
        self.entity_id = entity_id
        self.event_type = event_type
        self.payload = payload
        self.timestamp = time.time()

class EventStore:
    def __init__(self):
        # The append-only log
        self.events = []

    def save_event(self, event: DomainEvent):
        self.events.append(event)
        print(f"[EventStore] Appended: {event.event_type} | Data: {event.payload}")

    def get_events_for_entity(self, entity_id):
        # Fetching all events from the dawn of time for this specific ID
        return [e for e in self.events if e.entity_id == entity_id]

class ShoppingCartEntity:
    def __init__(self, cart_id):
        self.cart_id = cart_id
        self.items = []
        self.is_active = False

    def replay(self, events):
        """Reconstructs the state from a blank slate by replaying the history of events."""
        print(f"\n[ShoppingCartEntity] Replaying {len(events)} events to rebuild state...")
        self.items = []
        self.is_active = False
        
        for event in events:
            if event.event_type == "CartCreated":
                self.is_active = True
            elif event.event_type == "ItemAdded":
                self.items.append(event.payload["item"])
            elif event.event_type == "ItemRemoved":
                if event.payload["item"] in self.items:
                    self.items.remove(event.payload["item"])

    def print_state(self):
        print(f"-> Current Cart State: Active={self.is_active}, Items={self.items}\n")

if __name__ == "__main__":
    store = EventStore()
    cart_id = "CART_001"

    print("=== Event Sourcing Execution Flow ===\n")

    # Day 1: Actions happen
    store.save_event(DomainEvent(cart_id, "CartCreated", {}))
    store.save_event(DomainEvent(cart_id, "ItemAdded", {"item": "Laptop"}))
    store.save_event(DomainEvent(cart_id, "ItemAdded", {"item": "Mouse"}))

    # Day 2: The system needs to know the cart state
    # We do NOT read a row from a database. We rebuild it.
    history = store.get_events_for_entity(cart_id)
    cart = ShoppingCartEntity(cart_id)
    cart.replay(history)
    cart.print_state()

    # Day 3: User removes the mouse and adds a keyboard
    store.save_event(DomainEvent(cart_id, "ItemRemoved", {"item": "Mouse"}))
    store.save_event(DomainEvent(cart_id, "ItemAdded", {"item": "Keyboard"}))

    # Day 4: Rebuild state again
    history = store.get_events_for_entity(cart_id)
    cart_rebuilt = ShoppingCartEntity(cart_id)
    cart_rebuilt.replay(history)
    cart_rebuilt.print_state()
