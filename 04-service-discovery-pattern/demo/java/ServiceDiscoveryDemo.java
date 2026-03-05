import java.util.*;
import java.util.concurrent.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * ============================================================
 * SERVICE DISCOVERY PATTERN DEMO — Logistics System
 * ============================================================
 * 
 * Demonstrates how services register, discover each other,
 * and how the registry handles failures via heartbeats.
 * 
 * Components:
 * 1. ServiceRegistry — Central registry for service registration & discovery
 * 2. FleetService — Manages delivery fleet
 * 3. WarehouseService — Manages warehouse inventory (multiple instances)
 * 4. RouteService — Discovers fleet + warehouse to calculate routes
 */
public class ServiceDiscoveryDemo {

    // =============================================
    // Service Instance Model
    // =============================================

    static class ServiceInstance {
        String serviceName;
        String instanceId;
        String host;
        int port;
        String status; // HEALTHY, UNHEALTHY
        long lastHeartbeat;
        Map<String, String> metadata;

        ServiceInstance(String serviceName, String instanceId, String host, int port) {
            this.serviceName = serviceName;
            this.instanceId = instanceId;
            this.host = host;
            this.port = port;
            this.status = "HEALTHY";
            this.lastHeartbeat = System.currentTimeMillis();
            this.metadata = new HashMap<>();
        }

        String getUrl() {
            return "http://" + host + ":" + port;
        }

        @Override
        public String toString() {
            return String.format("Instance{%s @ %s:%d [%s]}", instanceId, host, port, status);
        }
    }

    // =============================================
    // 1. SERVICE REGISTRY — Central discovery hub
    // =============================================

    static class ServiceRegistry {
        // serviceName → list of instances
        private Map<String, List<ServiceInstance>> registry = new ConcurrentHashMap<>();
        private static final long HEARTBEAT_TIMEOUT_MS = 5000; // 5 seconds for demo

        /** Register a new service instance */
        synchronized ServiceInstance register(String serviceName, String instanceId, String host, int port) {
            ServiceInstance instance = new ServiceInstance(serviceName, instanceId, host, port);
            registry.computeIfAbsent(serviceName, k -> new CopyOnWriteArrayList<>()).add(instance);
            System.out.printf("  📋 Registry: Registered %s (%s:%d)%n", instanceId, host, port);
            return instance;
        }

        /** Deregister a service instance */
        synchronized void deregister(String serviceName, String instanceId) {
            List<ServiceInstance> instances = registry.get(serviceName);
            if (instances != null) {
                instances.removeIf(i -> i.instanceId.equals(instanceId));
                System.out.printf("  📋 Registry: Deregistered %s%n", instanceId);
            }
        }

        /** Receive heartbeat from a service */
        void heartbeat(String instanceId) {
            for (List<ServiceInstance> instances : registry.values()) {
                for (ServiceInstance instance : instances) {
                    if (instance.instanceId.equals(instanceId)) {
                        instance.lastHeartbeat = System.currentTimeMillis();
                        instance.status = "HEALTHY";
                        return;
                    }
                }
            }
        }

        /** Discover healthy instances of a service */
        List<ServiceInstance> discover(String serviceName) {
            List<ServiceInstance> instances = registry.getOrDefault(serviceName, new ArrayList<>());
            List<ServiceInstance> healthy = new ArrayList<>();
            for (ServiceInstance inst : instances) {
                if (inst.status.equals("HEALTHY")) {
                    healthy.add(inst);
                }
            }
            return healthy;
        }

        /** Check for dead instances (no heartbeat) */
        void healthCheck() {
            long now = System.currentTimeMillis();
            for (List<ServiceInstance> instances : registry.values()) {
                for (ServiceInstance instance : instances) {
                    if (now - instance.lastHeartbeat > HEARTBEAT_TIMEOUT_MS) {
                        if (instance.status.equals("HEALTHY")) {
                            instance.status = "UNHEALTHY";
                            System.out.printf("  ⚠️ Registry: %s marked UNHEALTHY (no heartbeat for %.1fs)%n",
                                    instance.instanceId, (now - instance.lastHeartbeat) / 1000.0);
                        }
                    }
                }
            }
        }

        /** Print the current state of the registry */
        void printRegistry() {
            System.out.println("\n  ┌─────────────────────────────────────────────────────┐");
            System.out.println("  │              SERVICE REGISTRY STATUS                 │");
            System.out.println("  ├──────────────┬─────────────────┬──────────┬──────────┤");
            System.out.println("  │ Service      │ Instance        │ Address  │ Status   │");
            System.out.println("  ├──────────────┼─────────────────┼──────────┼──────────┤");
            for (Map.Entry<String, List<ServiceInstance>> entry : registry.entrySet()) {
                for (ServiceInstance inst : entry.getValue()) {
                    System.out.printf("  │ %-12s │ %-15s │ %-8s │ %-8s │%n",
                            entry.getKey(), inst.instanceId, inst.host + ":" + inst.port, inst.status);
                }
            }
            System.out.println("  └──────────────┴─────────────────┴──────────┴──────────┘");
        }
    }

    // =============================================
    // 2. FLEET SERVICE
    // =============================================

    static class FleetService {
        private ServiceInstance registration;
        private ServiceRegistry registry;
        private List<Map<String, String>> vehicles = new ArrayList<>();

        FleetService(ServiceRegistry registry, String host, int port) {
            this.registry = registry;
            this.registration = registry.register("fleet", "fleet-1", host, port);

            vehicles.add(Map.of("id", "VH-001", "type", "Truck", "status", "Available", "driver", "John"));
            vehicles.add(Map.of("id", "VH-002", "type", "Van", "status", "In Transit", "driver", "Jane"));
            vehicles.add(Map.of("id", "VH-003", "type", "Truck", "status", "Available", "driver", "Mike"));
        }

        List<Map<String, String>> getAvailableVehicles() {
            return vehicles;
        }

        void sendHeartbeat() {
            registry.heartbeat(registration.instanceId);
        }
    }

    // =============================================
    // 3. WAREHOUSE SERVICE (Multiple instances)
    // =============================================

    static class WarehouseService {
        private ServiceInstance registration;
        private ServiceRegistry registry;
        private String warehouseName;
        private Map<String, Integer> inventory;

        WarehouseService(ServiceRegistry registry, String instanceId, String host, int port, String warehouseName) {
            this.registry = registry;
            this.warehouseName = warehouseName;
            this.registration = registry.register("warehouse", instanceId, host, port);
            this.inventory = new LinkedHashMap<>();
            inventory.put("Electronics", 500);
            inventory.put("Clothing", 1200);
            inventory.put("Furniture", 80);
        }

        Map<String, Object> getInventory() {
            Map<String, Object> result = new LinkedHashMap<>();
            result.put("warehouse", warehouseName);
            result.put("instance", registration.instanceId);
            result.put("inventory", new LinkedHashMap<>(inventory));
            return result;
        }

        void sendHeartbeat() {
            registry.heartbeat(registration.instanceId);
        }

        void stopHeartbeat() {
            // Simulates service going down — no more heartbeats
            System.out.printf("  💀 %s (%s) has stopped!%n", warehouseName, registration.instanceId);
        }
    }

    // =============================================
    // 4. ROUTE SERVICE — Uses discovery
    // =============================================

    static class RouteService {
        private ServiceRegistry registry;

        RouteService(ServiceRegistry registry) {
            this.registry = registry;
            registry.register("route", "route-1", "localhost", 8002);
        }

        /** Discovers fleet and warehouse services to plan a route */
        void planDeliveryRoute() {
            System.out.println("\n  🗺️ Route Service: Planning delivery route...");

            // Discover fleet service
            List<ServiceInstance> fleetInstances = registry.discover("fleet");
            if (fleetInstances.isEmpty()) {
                System.out.println("  ❌ Fleet Service not available!");
            } else {
                System.out.println("  ✅ Found Fleet Service: " + fleetInstances.get(0));
            }

            // Discover warehouse services
            List<ServiceInstance> warehouseInstances = registry.discover("warehouse");
            if (warehouseInstances.isEmpty()) {
                System.out.println("  ❌ No Warehouse Services available!");
            } else {
                System.out.println("  ✅ Found " + warehouseInstances.size() + " Warehouse instance(s):");
                for (ServiceInstance inst : warehouseInstances) {
                    System.out.println("     → " + inst);
                }
                // Client-side load balancing: pick random instance
                ServiceInstance selected = warehouseInstances.get(new Random().nextInt(warehouseInstances.size()));
                System.out.println("  🎯 Selected warehouse: " + selected.instanceId + " (round-robin)");
            }
        }
    }

    // =============================================
    // MAIN
    // =============================================

    public static void main(String[] args) throws InterruptedException {
        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║   SERVICE DISCOVERY PATTERN DEMO — Logistics System     ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝");

        ServiceRegistry registry = new ServiceRegistry();

        // ---- Phase 1: Services register ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 1: Service Registration");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        FleetService fleet = new FleetService(registry, "localhost", 8001);
        WarehouseService warehouse1 = new WarehouseService(registry, "warehouse-1", "localhost", 8003,
                "North Warehouse");
        WarehouseService warehouse2 = new WarehouseService(registry, "warehouse-2", "localhost", 8004,
                "South Warehouse");
        RouteService routeService = new RouteService(registry);

        registry.printRegistry();

        // ---- Phase 2: Discovery in action ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 2: Service Discovery");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        // Route service discovers other services
        routeService.planDeliveryRoute();

        // ---- Phase 3: Heartbeats ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 3: Heartbeat Mechanism");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        // All services send heartbeats
        fleet.sendHeartbeat();
        warehouse1.sendHeartbeat();
        warehouse2.sendHeartbeat();
        System.out.println("  💓 All services sent heartbeats");

        // ---- Phase 4: Simulate failure ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 4: Simulating Warehouse-2 Failure");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        warehouse2.stopHeartbeat();

        // Simulate time passing (heartbeat timeout)
        System.out.println("  ⏱️ Waiting for heartbeat timeout...");
        Thread.sleep(100);
        // Manually expire warehouse-2 for demo
        registry.registry.get("warehouse").stream()
                .filter(i -> i.instanceId.equals("warehouse-2"))
                .findFirst()
                .ifPresent(i -> i.lastHeartbeat = System.currentTimeMillis() - 10000);
        registry.healthCheck();

        // ---- Phase 5: Discovery after failure ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 5: Discovery After Failure");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        registry.printRegistry();
        routeService.planDeliveryRoute();

        // ---- Summary ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("✅ Demo complete! Service Discovery provided:");
        System.out.println("   • Auto-registration of services on startup");
        System.out.println("   • Dynamic discovery by service name (not URL)");
        System.out.println("   • Multiple instances for the same service");
        System.out.println("   • Failure detection via heartbeat timeout");
        System.out.println("   • Automatic removal of unhealthy instances");
    }
}
