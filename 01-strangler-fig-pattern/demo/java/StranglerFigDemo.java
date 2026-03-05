import java.util.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * ============================================================
 * STRANGLER FIG PATTERN DEMO — E-Commerce Order Migration
 * ============================================================
 * 
 * This demo simulates migrating an e-commerce monolith to
 * microservices using the Strangler Fig Pattern.
 * 
 * Components:
 *   1. LegacyMonolith   — The original monolith handling orders, inventory, payments
 *   2. NewOrderService   — The extracted microservice for orders
 *   3. FacadeRouter      — Routes traffic to monolith or new service
 *   4. FeatureFlag       — Controls which backend handles order requests
 * 
 * Flow:
 *   Client → FacadeRouter → (LegacyMonolith OR NewOrderService)
 */
public class StranglerFigDemo {

    // =============================================
    // Domain Models
    // =============================================
    
    static class Order {
        String id;
        String product;
        int quantity;
        double price;
        String status;
        String processedBy;
        String timestamp;

        Order(String id, String product, int quantity, double price) {
            this.id = id;
            this.product = product;
            this.quantity = quantity;
            this.price = price;
            this.status = "CREATED";
            this.timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        }

        @Override
        public String toString() {
            return String.format("  Order{id='%s', product='%s', qty=%d, price=%.2f, status='%s', processedBy='%s'}",
                    id, product, quantity, price, status, processedBy);
        }
    }

    static class InventoryItem {
        String product;
        int stock;

        InventoryItem(String product, int stock) {
            this.product = product;
            this.stock = stock;
        }
    }

    // =============================================
    // 1. LEGACY MONOLITH — Handles everything
    // =============================================
    
    static class LegacyMonolith {
        private Map<String, Order> orders = new HashMap<>();
        private Map<String, InventoryItem> inventory = new HashMap<>();
        private int orderCounter = 0;

        LegacyMonolith() {
            // Initialize inventory
            inventory.put("Laptop", new InventoryItem("Laptop", 50));
            inventory.put("Phone", new InventoryItem("Phone", 100));
            inventory.put("Tablet", new InventoryItem("Tablet", 30));
        }

        // Order operations (WILL BE MIGRATED)
        Order createOrder(String product, int quantity, double price) {
            String id = "MONO-" + (++orderCounter);
            Order order = new Order(id, product, quantity, price);
            order.processedBy = "LEGACY_MONOLITH";
            order.status = "CONFIRMED";
            orders.put(id, order);

            // Deduct inventory
            if (inventory.containsKey(product)) {
                inventory.get(product).stock -= quantity;
            }
            return order;
        }

        Order getOrder(String id) {
            Order order = orders.get(id);
            if (order != null) {
                order.processedBy = "LEGACY_MONOLITH";
            }
            return order;
        }

        List<Order> listOrders() {
            return new ArrayList<>(orders.values());
        }

        // Inventory operations (STAYS IN MONOLITH)
        int checkStock(String product) {
            InventoryItem item = inventory.get(product);
            return item != null ? item.stock : 0;
        }

        // Payment operations (STAYS IN MONOLITH)
        String processPayment(String orderId, double amount) {
            return String.format("  Payment of $%.2f for order %s processed by LEGACY_MONOLITH", amount, orderId);
        }
    }

    // =============================================
    // 2. NEW ORDER SERVICE — Extracted microservice
    // =============================================
    
    static class NewOrderService {
        private Map<String, Order> orders = new HashMap<>();
        private int orderCounter = 0;

        Order createOrder(String product, int quantity, double price) {
            String id = "SVC-" + (++orderCounter);
            Order order = new Order(id, product, quantity, price);
            order.processedBy = "NEW_ORDER_SERVICE";
            order.status = "CONFIRMED";

            // In real implementation, this would call Inventory Service via API
            // For demo, we just create the order
            orders.put(id, order);
            return order;
        }

        Order getOrder(String id) {
            Order order = orders.get(id);
            if (order != null) {
                order.processedBy = "NEW_ORDER_SERVICE";
            }
            return order;
        }

        List<Order> listOrders() {
            return new ArrayList<>(orders.values());
        }
    }

    // =============================================
    // 3. FEATURE FLAG — Controls routing
    // =============================================
    
    static class FeatureFlag {
        private Map<String, Boolean> flags = new HashMap<>();

        FeatureFlag() {
            // Initially, all routes go to monolith
            flags.put("orders.use_new_service", false);
        }

        boolean isEnabled(String flag) {
            return flags.getOrDefault(flag, false);
        }

        void enable(String flag) {
            flags.put(flag, true);
            System.out.println("  ⚡ Feature flag '" + flag + "' ENABLED — traffic routed to NEW service");
        }

        void disable(String flag) {
            flags.put(flag, false);
            System.out.println("  ⚡ Feature flag '" + flag + "' DISABLED — traffic routed to LEGACY monolith");
        }
    }

    // =============================================
    // 4. FACADE ROUTER — The strangler fig proxy
    // =============================================
    
    static class FacadeRouter {
        private LegacyMonolith monolith;
        private NewOrderService orderService;
        private FeatureFlag featureFlag;

        FacadeRouter(LegacyMonolith monolith, NewOrderService orderService, FeatureFlag featureFlag) {
            this.monolith = monolith;
            this.orderService = orderService;
            this.featureFlag = featureFlag;
        }

        /**
         * Routes order creation to the appropriate backend.
         * This is the KEY mechanism of the Strangler Fig Pattern.
         */
        Order createOrder(String product, int quantity, double price) {
            if (featureFlag.isEnabled("orders.use_new_service")) {
                System.out.println("  🔀 Facade routing → NEW Order Service");
                return orderService.createOrder(product, quantity, price);
            } else {
                System.out.println("  🔀 Facade routing → LEGACY Monolith");
                return monolith.createOrder(product, quantity, price);
            }
        }

        // Inventory always goes to monolith (not yet migrated)
        int checkStock(String product) {
            System.out.println("  🔀 Facade routing → LEGACY Monolith (inventory not migrated)");
            return monolith.checkStock(product);
        }

        // Payments always go to monolith (not yet migrated)
        String processPayment(String orderId, double amount) {
            System.out.println("  🔀 Facade routing → LEGACY Monolith (payments not migrated)");
            return monolith.processPayment(orderId, amount);
        }
    }

    // =============================================
    // MAIN — Demonstrates the migration phases
    // =============================================
    
    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║   STRANGLER FIG PATTERN DEMO — E-Commerce Migration     ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝");

        // Initialize components
        LegacyMonolith monolith = new LegacyMonolith();
        NewOrderService orderService = new NewOrderService();
        FeatureFlag featureFlag = new FeatureFlag();
        FacadeRouter facade = new FacadeRouter(monolith, orderService, featureFlag);

        // ---- PHASE 1: All traffic goes to Monolith ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 1: All traffic → Legacy Monolith");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        System.out.println("\n📦 Creating order via facade:");
        Order order1 = facade.createOrder("Laptop", 2, 999.99);
        System.out.println(order1);

        System.out.println("\n📦 Checking inventory via facade:");
        int stock = facade.checkStock("Laptop");
        System.out.println("  Laptop stock: " + stock);

        System.out.println("\n💳 Processing payment via facade:");
        System.out.println(facade.processPayment(order1.id, 1999.98));

        // ---- PHASE 2: Migrate Orders to new service ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 2: Enable new Order Service (flip feature flag)");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        featureFlag.enable("orders.use_new_service");

        System.out.println("\n📦 Creating order via facade (now routed to NEW service):");
        Order order2 = facade.createOrder("Phone", 1, 699.99);
        System.out.println(order2);

        System.out.println("\n📦 Creating another order:");
        Order order3 = facade.createOrder("Tablet", 3, 499.99);
        System.out.println(order3);

        // Inventory and payments STILL go to monolith
        System.out.println("\n📦 Checking inventory (still monolith):");
        System.out.println("  Phone stock: " + facade.checkStock("Phone"));

        System.out.println("\n💳 Processing payment (still monolith):");
        System.out.println(facade.processPayment(order2.id, 699.99));

        // ---- PHASE 3: Demonstrate rollback ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 3: Rollback demo (disable new service)");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        featureFlag.disable("orders.use_new_service");

        System.out.println("\n📦 Creating order (rolled back to monolith):");
        Order order4 = facade.createOrder("Laptop", 1, 999.99);
        System.out.println(order4);

        // ---- Summary ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("SUMMARY — Migration Results");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("\n  Orders processed by LEGACY monolith:");
        monolith.listOrders().forEach(o -> System.out.println("    " + o));
        System.out.println("\n  Orders processed by NEW order service:");
        orderService.listOrders().forEach(o -> System.out.println("    " + o));

        System.out.println("\n✅ Demo complete! The Strangler Fig Pattern enabled:");
        System.out.println("   • Zero-downtime migration of the Order module");
        System.out.println("   • Instant rollback via feature flag");
        System.out.println("   • Inventory & Payments remained in the monolith");
        System.out.println("   • Clients were unaware of the backend changes");
    }
}
