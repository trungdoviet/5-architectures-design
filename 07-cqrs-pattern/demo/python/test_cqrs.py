import time

class WriteDatabase:
    def __init__(self):
        self.users = {}

    def save(self, user_id, user_data):
        self.users[user_id] = user_data
        print(f"[WriteDB] Saved complete domain entity: {user_data}")

class ReadDatabase:
    def __init__(self):
        # Optimized for fast reads (denormalized)
        self.user_views = {}

    def save_view(self, user_id, display_card):
        self.user_views[user_id] = display_card
        print(f"[ReadDB] Saved flat View Model: {display_card}")

    def get_user_card(self, user_id):
        return self.user_views.get(user_id)

class EventBus:
    def __init__(self):
        self.subscribers = []

    def subscribe(self, callback):
        self.subscribers.append(callback)

    def publish(self, event_type, payload):
        print(f"[EventBus] Emitting event: {event_type}...")
        for sub in self.subscribers:
            sub(event_type, payload)

class CommandService:
    def __init__(self, write_db, event_bus):
        self.db = write_db
        self.bus = event_bus

    def create_user(self, user_id, first_name, last_name, email):
        # 1. Complex business logic and validation here
        if not "@" in email:
            raise ValueError("Invalid email format")
            
        user_entity = {
            "id": user_id,
            "first_name": first_name, 
            "last_name": last_name, 
            "email": email, 
            "status": "ACTIVE",
            "created_at": time.time()
        }
        
        # 2. Save to write db
        self.db.save(user_id, user_entity)
        
        # 3. Publish Domain Event
        self.bus.publish("UserCreated", user_entity)

class QueryService:
    def __init__(self, read_db):
        self.db = read_db

    def get_display_card(self, user_id):
        print(f"[QueryService] Fast fetching display card for {user_id}...")
        return self.db.get_user_card(user_id)

    def handle_event(self, event_type, payload):
        # Synchronize Read Model when Write Model changes
        if event_type == "UserCreated":
            user_id = payload["id"]
            # Creating a flat projection
            display_card = {
                "id": user_id,
                "full_name": f"{payload['first_name']} {payload['last_name']}",
                "contact_email": payload["email"]
            }
            self.db.save_view(user_id, display_card)

if __name__ == "__main__":
    write_db = WriteDatabase()
    read_db = ReadDatabase()
    event_bus = EventBus()

    command_api = CommandService(write_db, event_bus)
    query_api = QueryService(read_db)

    # Wire event bus to query service to simulate async syncing
    event_bus.subscribe(query_api.handle_event)

    print("=== CQRS Execution Flow ===\n")
    print("1. Submitting Command -> Create User")
    command_api.create_user("U123", "John", "Doe", "john@example.com")
    
    print("\n2. Querying Read Model -> Fetch User")
    card = query_api.get_display_card("U123")
    print(f"Result: {card}")
