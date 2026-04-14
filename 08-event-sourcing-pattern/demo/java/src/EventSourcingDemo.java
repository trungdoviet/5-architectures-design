import java.util.ArrayList;
import java.util.List;
import java.util.stream.Collectors;

class DomainEvent {
    String entityId;
    String eventType;
    String payload; // Using a simple string payload for demo brevity
    long timestamp;

    public DomainEvent(String id, String type, String data) {
        this.entityId = id; this.eventType = type; this.payload = data; this.timestamp = System.currentTimeMillis();
    }
}

class EventStore {
    private List<DomainEvent> events = new ArrayList<>();

    public void saveEvent(DomainEvent e) {
        events.add(e);
        System.out.println("[EventStore] Appended: " + e.eventType + " | Data: " + e.payload);
    }

    public List<DomainEvent> getEventsForEntity(String entityId) {
        return events.stream().filter(e -> e.entityId.equals(entityId)).collect(Collectors.toList());
    }
}

class ShoppingCartEntity {
    private String cartId;
    private List<String> items = new ArrayList<>();
    private boolean isActive = false;

    public ShoppingCartEntity(String cartId) { this.cartId = cartId; }

    public void replay(List<DomainEvent> eventHistory) {
        System.out.println("\n[ShoppingCartEntity] Replaying " + eventHistory.size() + " events to rebuild state...");
        items.clear();
        isActive = false;

        for (DomainEvent event : eventHistory) {
            switch (event.eventType) {
                case "CartCreated":
                    isActive = true;
                    break;
                case "ItemAdded":
                    items.add(event.payload);
                    break;
                case "ItemRemoved":
                    items.remove(event.payload);
                    break;
            }
        }
    }

    public void printState() {
        System.out.println("-> Current Cart State: Active=" + isActive + ", Items=" + items + "\n");
    }
}

public class EventSourcingDemo {
    public static void main(String[] args) {
        EventStore store = new EventStore();
        String cartId = "CART_001";

        System.out.println("=== Event Sourcing Execution Flow ===\n");

        // Day 1
        store.saveEvent(new DomainEvent(cartId, "CartCreated", ""));
        store.saveEvent(new DomainEvent(cartId, "ItemAdded", "Laptop"));
        store.saveEvent(new DomainEvent(cartId, "ItemAdded", "Mouse"));

        // Day 2: Rebuild State
        List<DomainEvent> history = store.getEventsForEntity(cartId);
        ShoppingCartEntity cart = new ShoppingCartEntity(cartId);
        cart.replay(history);
        cart.printState();

        // Day 3: Changes
        store.saveEvent(new DomainEvent(cartId, "ItemRemoved", "Mouse"));
        store.saveEvent(new DomainEvent(cartId, "ItemAdded", "Keyboard"));

        // Day 4: Rebuild State Again
        history = store.getEventsForEntity(cartId);
        cart.replay(history);
        cart.printState();
    }
}
