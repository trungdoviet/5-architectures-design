import time
import json

class LegacyApplication:
    """A legacy service that knows nothing about modern logging or metrics."""
    def handle_request(self, user_id):
        # Barebones stdout logging
        print(f"[LegacyApp] Processing request internally for user: {user_id}")
        time.sleep(0.2)
        return "Legacy Success Data"

class SidecarProxy:
    """A sidecar that attaches to the legacy app to add tracing, metrics, and JSON logging."""
    def __init__(self, legacy_app):
        self.app = legacy_app

    def handle_request(self, user_id):
        start_time = time.time()
        
        # 1. Cross-cutting concern: Add tracing ID
        trace_id = f"TRACE-{int(start_time * 1000)}"
        
        try:
            # 2. Forward traffic to the primary application
            response = self.app.handle_request(user_id)
            status = "SUCCESS"
        except Exception as e:
            response = str(e)
            status = "ERROR"
            
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        # 3. Cross-cutting concern: Structured JSON Logging & Metrics
        log_entry = {
            "timestamp": start_time,
            "trace_id": trace_id,
            "user_id": user_id,
            "latency_ms": elapsed_ms,
            "status": status,
            "app_response": response
        }
        
        print("\n[Sidecar] Shipping structured log to central collector:")
        print(json.dumps(log_entry, indent=2))
        
        return response

if __name__ == "__main__":
    legacy = LegacyApplication()
    sidecar = SidecarProxy(legacy)

    print("=== Sidecar Pattern Execution Flow ===\n")
    print("Client sending request to Service Proxy (Sidecar)...")
    
    # Client only talks to the Sidecar, which abstracts the connection to the Legacy App
    sidecar_response = sidecar.handle_request(user_id="U-999")
    
    print(f"\nFinal Response sent to Client: {sidecar_response}")
