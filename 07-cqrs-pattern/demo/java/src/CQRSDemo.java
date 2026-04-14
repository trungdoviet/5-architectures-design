import java.util.HashMap;
import java.util.Map;
import java.util.List;
import java.util.ArrayList;

class WriteDatabase {
    private Map<String, UserEntity> users = new HashMap<>();
    public void save(UserEntity user) {
        users.put(user.id, user);
        System.out.println("[WriteDB] Saved complete domain entity: " + user.id);
    }
}

class ReadDatabase {
    private Map<String, UserView> userViews = new HashMap<>();
    public void saveView(UserView view) {
        userViews.put(view.id, view);
        System.out.println("[ReadDB] Saved flat View Model for: " + view.fullName);
    }
    public UserView getUserCard(String id) {
        return userViews.get(id);
    }
}

class UserEntity {
    String id, firstName, lastName, email, status;
    long createdAt;
    public UserEntity(String i, String f, String l, String e) {
        id = i; firstName = f; lastName = l; email = e; status = "ACTIVE"; createdAt = System.currentTimeMillis();
    }
}

class UserView {
    String id, fullName, contactEmail;
    public UserView(String i, String n, String e) { id = i; fullName = n; contactEmail = e; }
}

interface EventListener {
    void onEvent(String eventType, UserEntity payload);
}

class EventBus {
    private List<EventListener> subscribers = new ArrayList<>();
    public void subscribe(EventListener listener) { subscribers.add(listener); }
    public void publish(String eventType, UserEntity payload) {
        System.out.println("[EventBus] Emitting event: " + eventType + "...");
        for (EventListener sub : subscribers) { sub.onEvent(eventType, payload); }
    }
}

class CommandService {
    private WriteDatabase db; private EventBus bus;
    public CommandService(WriteDatabase db, EventBus bus) { this.db = db; this.bus = bus; }
    public void createUser(String id, String first, String last, String email) {
        if (!email.contains("@")) throw new IllegalArgumentException("Invalid email format");
        UserEntity entity = new UserEntity(id, first, last, email);
        db.save(entity);
        bus.publish("UserCreated", entity);
    }
}

class QueryService implements EventListener {
    private ReadDatabase db;
    public QueryService(ReadDatabase db) { this.db = db; }
    public UserView getDisplayCard(String id) {
        System.out.println("[QueryService] Fast fetching display card for " + id + "...");
        return db.getUserCard(id);
    }
    @Override
    public void onEvent(String eventType, UserEntity payload) {
        if ("UserCreated".equals(eventType)) {
            UserView view = new UserView(payload.id, payload.firstName + " " + payload.lastName, payload.email);
            db.saveView(view);
        }
    }
}

public class CQRSDemo {
    public static void main(String[] args) {
        WriteDatabase writeDb = new WriteDatabase();
        ReadDatabase readDb = new ReadDatabase();
        EventBus bus = new EventBus();

        CommandService commandApi = new CommandService(writeDb, bus);
        QueryService queryApi = new QueryService(readDb);
        bus.subscribe(queryApi); // Wire sync

        System.out.println("=== CQRS Execution Flow ===\n");
        System.out.println("1. Submitting Command -> Create User");
        commandApi.createUser("U123", "John", "Doe", "john@example.com");

        System.out.println("\n2. Querying Read Model -> Fetch User");
        UserView card = queryApi.getDisplayCard("U123");
        System.out.println("Result: " + card.fullName + " | " + card.contactEmail);
    }
}
