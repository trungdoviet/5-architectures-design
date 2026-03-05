import java.util.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * ============================================================
 * CIRCUIT BREAKER PATTERN DEMO — Medical Appointment System
 * ============================================================
 * 
 * Demonstrates how a circuit breaker protects the Booking
 * Service from cascading failures when the Payment Service
 * goes down.
 * 
 * Components:
 * 1. CircuitBreaker — State machine (CLOSED/OPEN/HALF_OPEN)
 * 2. PaymentService — External service that can fail
 * 3. BookingService — Uses circuit breaker to protect payment calls
 */
public class CircuitBreakerDemo {

    // =============================================
    // Circuit Breaker States
    // =============================================

    enum CircuitState {
        CLOSED, OPEN, HALF_OPEN
    }

    // =============================================
    // Circuit Breaker Implementation
    // =============================================

    static class CircuitBreaker {
        private CircuitState state = CircuitState.CLOSED;
        private int failureCount = 0;
        private int successCount = 0;
        private final int failureThreshold;
        private final long openTimeoutMs;
        private long lastFailureTime = 0;
        private final String name;
        private List<String> stateLog = new ArrayList<>();

        CircuitBreaker(String name, int failureThreshold, long openTimeoutMs) {
            this.name = name;
            this.failureThreshold = failureThreshold;
            this.openTimeoutMs = openTimeoutMs;
            logTransition("INITIALIZED", CircuitState.CLOSED);
        }

        /** Check if the circuit allows the request */
        boolean allowRequest() {
            switch (state) {
                case CLOSED:
                    return true;
                case OPEN:
                    // Check if timeout has elapsed → move to HALF_OPEN
                    if (System.currentTimeMillis() - lastFailureTime >= openTimeoutMs) {
                        transition(CircuitState.HALF_OPEN);
                        return true; // Allow one test request
                    }
                    return false;
                case HALF_OPEN:
                    return true; // Allow test request
                default:
                    return false;
            }
        }

        /** Record a successful call */
        void recordSuccess() {
            switch (state) {
                case HALF_OPEN:
                    successCount++;
                    transition(CircuitState.CLOSED);
                    failureCount = 0;
                    break;
                case CLOSED:
                    failureCount = 0; // Reset on success
                    break;
                default:
                    break;
            }
        }

        /** Record a failed call */
        void recordFailure() {
            failureCount++;
            lastFailureTime = System.currentTimeMillis();

            switch (state) {
                case CLOSED:
                    if (failureCount >= failureThreshold) {
                        transition(CircuitState.OPEN);
                    } else {
                        System.out.printf("  ⚠️ [%s] Failure %d/%d (circuit still CLOSED)%n",
                                name, failureCount, failureThreshold);
                    }
                    break;
                case HALF_OPEN:
                    transition(CircuitState.OPEN); // Test failed, go back to OPEN
                    break;
                default:
                    break;
            }
        }

        private void transition(CircuitState newState) {
            CircuitState oldState = this.state;
            this.state = newState;
            String msg = String.format("%s → %s", oldState, newState);
            logTransition(msg, newState);
            System.out.printf("  🔄 [%s] Circuit state: %s → %s%n", name, oldState, newState);
        }

        private void logTransition(String msg, CircuitState state) {
            stateLog.add(String.format("[%s] %s (state: %s, failures: %d)",
                    LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss.SSS")),
                    msg, state, failureCount));
        }

        CircuitState getState() {
            return state;
        }

        List<String> getStateLog() {
            return stateLog;
        }
    }

    // =============================================
    // Payment Service (Unreliable)
    // =============================================

    static class PaymentService {
        private boolean isHealthy = true;

        /** Simulate payment processing */
        String processPayment(String appointmentId, double amount) throws RuntimeException {
            if (!isHealthy) {
                throw new RuntimeException("Payment Service is DOWN! Connection refused.");
            }
            return String.format("Payment of $%.2f for appointment %s processed successfully.", amount, appointmentId);
        }

        void setHealthy(boolean healthy) {
            this.isHealthy = healthy;
            System.out.printf("  %s Payment Service is now %s%n",
                    healthy ? "✅" : "❌", healthy ? "HEALTHY" : "DOWN");
        }
    }

    // =============================================
    // Booking Service (With Circuit Breaker)
    // =============================================

    static class BookingService {
        private CircuitBreaker circuitBreaker;
        private PaymentService paymentService;
        private int appointmentCounter = 0;

        BookingService(PaymentService paymentService, CircuitBreaker circuitBreaker) {
            this.paymentService = paymentService;
            this.circuitBreaker = circuitBreaker;
        }

        Map<String, String> bookAppointment(String patientName, String doctor, double fee) {
            String appointmentId = "APT-" + (++appointmentCounter);
            Map<String, String> result = new LinkedHashMap<>();
            result.put("appointment_id", appointmentId);
            result.put("patient", patientName);
            result.put("doctor", doctor);
            result.put("fee", String.format("$%.2f", fee));

            // Try to process payment through the circuit breaker
            if (circuitBreaker.allowRequest()) {
                try {
                    String paymentResult = paymentService.processPayment(appointmentId, fee);
                    circuitBreaker.recordSuccess();
                    result.put("payment_status", "PAID");
                    result.put("payment_detail", paymentResult);
                    result.put("circuit_state", circuitBreaker.getState().name());
                } catch (RuntimeException e) {
                    circuitBreaker.recordFailure();
                    result.put("payment_status", "DEFERRED");
                    result.put("payment_detail", "⚠️ Payment will be retried later");
                    result.put("circuit_state", circuitBreaker.getState().name());
                    result.put("fallback", "Appointment confirmed. Payment will be processed when service recovers.");
                }
            } else {
                // Circuit is OPEN — use fallback immediately
                result.put("payment_status", "DEFERRED");
                result.put("payment_detail", "🔴 Circuit OPEN — payment skipped (fast fail)");
                result.put("circuit_state", circuitBreaker.getState().name());
                result.put("fallback", "Appointment confirmed. Payment pending service recovery.");
            }

            return result;
        }
    }

    // =============================================
    // MAIN
    // =============================================

    public static void main(String[] args) throws InterruptedException {
        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║  CIRCUIT BREAKER PATTERN DEMO — Medical Appointments    ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝");

        // Initialize components
        PaymentService paymentService = new PaymentService();
        CircuitBreaker circuitBreaker = new CircuitBreaker("PaymentCircuit", 3, 2000); // 3 failures, 2s timeout
        BookingService bookingService = new BookingService(paymentService, circuitBreaker);

        // ---- Phase 1: Normal operation ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 1: Normal Operation (Circuit CLOSED)");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        printBooking(bookingService.bookAppointment("Alice", "Dr. Smith", 150.00));
        printBooking(bookingService.bookAppointment("Bob", "Dr. Jones", 200.00));

        // ---- Phase 2: Payment service goes down ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 2: Payment Service Goes DOWN");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        paymentService.setHealthy(false);

        // These will fail and count toward the threshold
        System.out.println("\n  Booking appointments while payment is down...");
        printBooking(bookingService.bookAppointment("Charlie", "Dr. Smith", 175.00)); // Failure 1
        printBooking(bookingService.bookAppointment("Diana", "Dr. Lee", 250.00)); // Failure 2
        printBooking(bookingService.bookAppointment("Eve", "Dr. Jones", 300.00)); // Failure 3 → OPEN!

        // ---- Phase 3: Circuit OPEN (fast fail) ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 3: Circuit OPEN — Fast Fail with Fallback");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        // These will fail INSTANTLY (no call to payment service)
        printBooking(bookingService.bookAppointment("Frank", "Dr. Smith", 150.00));
        printBooking(bookingService.bookAppointment("Grace", "Dr. Lee", 200.00));

        // ---- Phase 4: Recovery ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("PHASE 4: Payment Service Recovers (HALF-OPEN → CLOSED)");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        paymentService.setHealthy(true);

        // Wait for circuit timeout to allow HALF-OPEN transition
        System.out.println("  ⏱️ Waiting for circuit timeout (2 seconds)...");
        Thread.sleep(2100);

        // This request will test the circuit (HALF-OPEN → CLOSED)
        System.out.println("\n  First request after timeout (HALF-OPEN test):");
        printBooking(bookingService.bookAppointment("Henry", "Dr. Smith", 175.00));

        // Back to normal
        System.out.println("\n  Normal operation resumed:");
        printBooking(bookingService.bookAppointment("Iris", "Dr. Jones", 225.00));

        // ---- State Log ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("Circuit Breaker State Transition Log:");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        for (String log : circuitBreaker.getStateLog()) {
            System.out.println("  " + log);
        }

        System.out.println("\n✅ Demo complete! The Circuit Breaker provided:");
        System.out.println("   • Automatic failure detection (3 failures → OPEN)");
        System.out.println("   • Fast-fail fallback (no wasted time on failed calls)");
        System.out.println("   • Self-healing (HALF-OPEN test → CLOSED on success)");
        System.out.println("   • Appointments were NEVER lost (fallback: deferred payment)");
    }

    static void printBooking(Map<String, String> booking) {
        System.out.println("\n  📋 Appointment: " + booking.get("appointment_id"));
        booking.forEach((k, v) -> {
            if (!k.equals("appointment_id")) {
                System.out.println("     " + k + ": " + v);
            }
        });
    }
}
