class PaymentService {
    public boolean processPayment(String orderId, double amount) {
        System.out.println("[PaymentService] Processing payment of $" + amount + " for order " + orderId + "...");
        delay();
        return true;
    }

    public boolean refundPayment(String orderId, double amount) {
        System.out.println("[PaymentService] ⚠️ COMPENSATING ACTION: Refunding $" + amount + " for order " + orderId + "...");
        delay();
        return true;
    }

    private void delay() {
        try { Thread.sleep(500); } catch (InterruptedException e) { }
    }
}

class InventoryService {
    private int stock;

    public InventoryService(int initialStock) {
        this.stock = initialStock;
    }

    public boolean reserveStock(String orderId, String itemId, int quantity) {
        System.out.println("[InventoryService] Attempting to reserve " + quantity + " units of item " + itemId + " for order " + orderId + "...");
        delay();
        if (stock >= quantity) {
            stock -= quantity;
            System.out.println("[InventoryService] Successfully reserved " + quantity + " units. Remaining stock: " + stock);
            return true;
        } else {
            System.out.println("[InventoryService] ❌ FAILED: Out of stock! Remaining: " + stock + ", Requested: " + quantity);
            return false;
        }
    }

    private void delay() {
        try { Thread.sleep(500); } catch (InterruptedException e) { }
    }
}

class OrderOrchestrator {
    private PaymentService paymentService;
    private InventoryService inventoryService;

    public OrderOrchestrator(PaymentService paymentService, InventoryService inventoryService) {
        this.paymentService = paymentService;
        this.inventoryService = inventoryService;
    }

    public boolean createOrder(String orderId, String itemId, int quantity, double amount) {
        System.out.println("\n--- Starting Saga for Order " + orderId + " ---");

        // Step 1: Process Payment
        boolean paymentSuccess = paymentService.processPayment(orderId, amount);
        if (!paymentSuccess) {
            System.out.println("--- Saga Failed at Payment for Order " + orderId + ". No compensation needed. ---");
            return false;
        }

        // Step 2: Reserve Inventory
        boolean inventorySuccess = inventoryService.reserveStock(orderId, itemId, quantity);
        if (!inventorySuccess) {
            System.out.println("[Orchestrator] Inventory reservation failed, initiating compensation...");
            // COMPENSATING ACTION
            paymentService.refundPayment(orderId, amount);
            System.out.println("--- Saga Failed and Compensated for Order " + orderId + " ---");
            return false;
        }

        System.out.println("--- Saga Completed Successfully for Order " + orderId + " ---");
        return true;
    }
}

public class SagaDemo {
    public static void main(String[] args) {
        PaymentService paymentService = new PaymentService();
        InventoryService inventoryService = new InventoryService(2); // Start with 2 items
        OrderOrchestrator orchestrator = new OrderOrchestrator(paymentService, inventoryService);

        System.out.println("=== SCENARIO 1: Happy Path ===");
        orchestrator.createOrder("101", "Laptop", 1, 1000.0);

        System.out.println("\n=== SCENARIO 2: Failure Path (Out of Stock) ===");
        orchestrator.createOrder("102", "Laptop", 2, 2000.0);
    }
}
