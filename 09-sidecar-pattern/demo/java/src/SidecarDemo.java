class LegacyApplication {
    // A legacy service that knows nothing about modern logging or metrics.
    public String handleRequest(String userId) {
        System.out.println("[LegacyApp] Processing request internally for user: " + userId);
        try { Thread.sleep(200); } catch (Exception e) {}
        return "Legacy Success Data";
    }
}

class SidecarProxy {
    // A sidecar that attaches to the legacy app to add tracing, metrics, and JSON logging.
    private LegacyApplication app;

    public SidecarProxy(LegacyApplication app) {
        this.app = app;
    }

    public String handleRequest(String userId) {
        long startTime = System.currentTimeMillis();
        String traceId = "TRACE-" + startTime;
        
        String response;
        String status;
        
        try {
            response = app.handleRequest(userId);
            status = "SUCCESS";
        } catch (Exception e) {
            response = e.getMessage();
            status = "ERROR";
        }
        
        long elapsedMs = System.currentTimeMillis() - startTime;
        
        System.out.println("\n[Sidecar] Shipping structured log to central collector:");
        System.out.println("{");
        System.out.println("  \"timestamp\": " + startTime + ",");
        System.out.println("  \"trace_id\": \"" + traceId + "\",");
        System.out.println("  \"user_id\": \"" + userId + "\",");
        System.out.println("  \"latency_ms\": " + elapsedMs + ",");
        System.out.println("  \"status\": \"" + status + "\",");
        System.out.println("  \"app_response\": \"" + response + "\"");
        System.out.println("}");
        
        return response;
    }
}

public class SidecarDemo {
    public static void main(String[] args) {
        LegacyApplication legacy = new LegacyApplication();
        SidecarProxy sidecar = new SidecarProxy(legacy);

        System.out.println("=== Sidecar Pattern Execution Flow ===\n");
        System.out.println("Client sending request to Service Proxy (Sidecar)...");
        
        String response = sidecar.handleRequest("U-999");
        
        System.out.println("\nFinal Response sent to Client: " + response);
    }
}
