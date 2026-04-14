import time

class PaymentService:
    def process_payment(self, order_id, amount):
        print(f"[PaymentService] Processing payment of ${amount} for order {order_id}...")
        time.sleep(0.5)
        return True

    def refund_payment(self, order_id, amount):
        print(f"[PaymentService] ⚠️ COMPENSATING ACTION: Refunding ${amount} for order {order_id}...")
        time.sleep(0.5)
        return True

class InventoryService:
    def __init__(self, stock):
        self.stock = stock

    def reserve_stock(self, order_id, item_id, quantity):
        print(f"[InventoryService] Attempting to reserve {quantity} units of item {item_id} for order {order_id}...")
        time.sleep(0.5)
        if self.stock >= quantity:
            self.stock -= quantity
            print(f"[InventoryService] Successfully reserved {quantity} units. Remaining stock: {self.stock}")
            return True
        else:
            print(f"[InventoryService] ❌ FAILED: Out of stock! Remaining: {self.stock}, Requested: {quantity}")
            return False

class OrderOrchestrator:
    def __init__(self, payment_service, inventory_service):
        self.payment_service = payment_service
        self.inventory_service = inventory_service
        self.orders = {}

    def create_order(self, order_id, item_id, quantity, amount):
        print(f"\n--- Starting Saga for Order {order_id} ---")
        self.orders[order_id] = "PENDING"

        # Step 1: Process Payment
        payment_success = self.payment_service.process_payment(order_id, amount)
        if not payment_success:
            self.orders[order_id] = "FAILED"
            print(f"--- Saga Failed at Payment for Order {order_id}. No compensation needed. ---")
            return False

        # Step 2: Reserve Inventory
        inventory_success = self.inventory_service.reserve_stock(order_id, item_id, quantity)
        if not inventory_success:
            print(f"[Orchestrator] Inventory reservation failed, initiating compensation...")
            # COMPENSATING ACTION
            self.payment_service.refund_payment(order_id, amount)
            self.orders[order_id] = "CANCELLED"
            print(f"--- Saga Failed and Compensated for Order {order_id} ---")
            return False

        self.orders[order_id] = "APPROVED"
        print(f"--- Saga Completed Successfully for Order {order_id} ---")
        return True

if __name__ == "__main__":
    payment = PaymentService()
    # Inventory starts with 2 items
    inventory = InventoryService(stock=2)
    orchestrator = OrderOrchestrator(payment, inventory)

    print("=== SCENARIO 1: Happy Path ===")
    orchestrator.create_order(order_id="101", item_id="Laptop", quantity=1, amount=1000)

    print("\n=== SCENARIO 2: Failure Path (Out of Stock) ===")
    # Attempting to buy 2 will fail because only 1 is left.
    orchestrator.create_order(order_id="102", item_id="Laptop", quantity=2, amount=2000)
