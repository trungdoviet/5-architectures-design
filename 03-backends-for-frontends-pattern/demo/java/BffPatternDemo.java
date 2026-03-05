import java.util.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

/**
 * ============================================================
 * BACKENDS FOR FRONTENDS (BFF) PATTERN DEMO — Banking App
 * ============================================================
 * 
 * Demonstrates how Web and Mobile platforms get different
 * optimized responses from their dedicated BFF backends,
 * while sharing the same core services.
 * 
 * Components:
 * 1. AccountService — Core: manages bank accounts
 * 2. TransactionService — Core: manages transactions
 * 3. WebBFF — Tailored API for web dashboard
 * 4. MobileBFF — Tailored API for mobile app
 */
public class BffPatternDemo {

    // =============================================
    // Domain Models
    // =============================================

    static class Account {
        String id, name, type;
        double balance;
        String currency;

        Account(String id, String name, String type, double balance) {
            this.id = id;
            this.name = name;
            this.type = type;
            this.balance = balance;
            this.currency = "USD";
        }
    }

    static class Transaction {
        String id, accountId, description, category;
        double amount;
        String type; // CREDIT or DEBIT
        String date;

        Transaction(String id, String accountId, String description, double amount, String type, String category,
                String date) {
            this.id = id;
            this.accountId = accountId;
            this.description = description;
            this.amount = amount;
            this.type = type;
            this.category = category;
            this.date = date;
        }
    }

    // =============================================
    // 1. CORE: Account Service
    // =============================================

    static class AccountService {
        private Map<String, Account> accounts = new LinkedHashMap<>();

        AccountService() {
            accounts.put("acc-1", new Account("acc-1", "Main Checking", "CHECKING", 15420.50));
            accounts.put("acc-2", new Account("acc-2", "Savings", "SAVINGS", 52000.00));
            accounts.put("acc-3", new Account("acc-3", "Credit Card", "CREDIT", -3200.75));
        }

        Account getAccount(String id) {
            return accounts.get(id);
        }

        List<Account> getAllAccounts() {
            return new ArrayList<>(accounts.values());
        }

        double getTotalBalance() {
            return accounts.values().stream().mapToDouble(a -> a.balance).sum();
        }
    }

    // =============================================
    // 2. CORE: Transaction Service
    // =============================================

    static class TransactionService {
        private List<Transaction> transactions = new ArrayList<>();

        TransactionService() {
            transactions.add(
                    new Transaction("txn-1", "acc-1", "Salary Deposit", 5000.00, "CREDIT", "Income", "2024-01-15"));
            transactions.add(new Transaction("txn-2", "acc-1", "Grocery Store", -85.50, "DEBIT", "Food", "2024-01-14"));
            transactions.add(
                    new Transaction("txn-3", "acc-1", "Electric Bill", -120.00, "DEBIT", "Utilities", "2024-01-13"));
            transactions.add(new Transaction("txn-4", "acc-1", "Coffee Shop", -5.75, "DEBIT", "Food", "2024-01-13"));
            transactions.add(new Transaction("txn-5", "acc-2", "Interest", 42.50, "CREDIT", "Income", "2024-01-12"));
            transactions.add(
                    new Transaction("txn-6", "acc-1", "Online Shopping", -249.99, "DEBIT", "Shopping", "2024-01-11"));
            transactions.add(new Transaction("txn-7", "acc-3", "Restaurant", -65.00, "DEBIT", "Food", "2024-01-10"));
            transactions.add(
                    new Transaction("txn-8", "acc-1", "Freelance Payment", 1200.00, "CREDIT", "Income", "2024-01-09"));
            transactions
                    .add(new Transaction("txn-9", "acc-1", "Gas Station", -45.00, "DEBIT", "Transport", "2024-01-08"));
            transactions
                    .add(new Transaction("txn-10", "acc-1", "Netflix", -15.99, "DEBIT", "Entertainment", "2024-01-07"));
        }

        List<Transaction> getByAccount(String accountId) {
            List<Transaction> result = new ArrayList<>();
            for (Transaction t : transactions) {
                if (t.accountId.equals(accountId))
                    result.add(t);
            }
            return result;
        }

        List<Transaction> getAll() {
            return transactions;
        }

        Map<String, Double> getSpendingByCategory() {
            Map<String, Double> categories = new LinkedHashMap<>();
            for (Transaction t : transactions) {
                if (t.amount < 0) {
                    categories.merge(t.category, Math.abs(t.amount), Double::sum);
                }
            }
            return categories;
        }

        double getMonthlyIncome() {
            return transactions.stream().filter(t -> t.amount > 0).mapToDouble(t -> t.amount).sum();
        }

        double getMonthlyExpenses() {
            return transactions.stream().filter(t -> t.amount < 0).mapToDouble(t -> Math.abs(t.amount)).sum();
        }
    }

    // =============================================
    // 3. WEB BFF — Rich dashboard data
    // =============================================

    static class WebBFF {
        private AccountService accountService;
        private TransactionService transactionService;

        WebBFF(AccountService as, TransactionService ts) {
            this.accountService = as;
            this.transactionService = ts;
        }

        /** Returns rich dashboard data for the web frontend */
        Map<String, Object> getDashboard() {
            Map<String, Object> dashboard = new LinkedHashMap<>();

            // Account summary with all details
            List<Map<String, Object>> accountDetails = new ArrayList<>();
            for (Account acc : accountService.getAllAccounts()) {
                Map<String, Object> detail = new LinkedHashMap<>();
                detail.put("id", acc.id);
                detail.put("name", acc.name);
                detail.put("type", acc.type);
                detail.put("balance", String.format("$%.2f", acc.balance));
                detail.put("currency", acc.currency);
                detail.put("recent_transactions", transactionService.getByAccount(acc.id).size());
                accountDetails.add(detail);
            }
            dashboard.put("accounts", accountDetails);
            dashboard.put("total_balance", String.format("$%.2f", accountService.getTotalBalance()));

            // Full transaction history (web has space for tables)
            List<Map<String, String>> txnDetails = new ArrayList<>();
            for (Transaction t : transactionService.getAll()) {
                Map<String, String> txn = new LinkedHashMap<>();
                txn.put("id", t.id);
                txn.put("description", t.description);
                txn.put("amount", String.format("$%.2f", t.amount));
                txn.put("type", t.type);
                txn.put("category", t.category);
                txn.put("date", t.date);
                txn.put("account", t.accountId);
                txnDetails.add(txn);
            }
            dashboard.put("transaction_history", txnDetails);

            // Analytics for charts
            Map<String, Object> analytics = new LinkedHashMap<>();
            analytics.put("spending_by_category", transactionService.getSpendingByCategory());
            analytics.put("monthly_income", String.format("$%.2f", transactionService.getMonthlyIncome()));
            analytics.put("monthly_expenses", String.format("$%.2f", transactionService.getMonthlyExpenses()));
            analytics.put("savings_rate", String.format("%.1f%%",
                    (transactionService.getMonthlyIncome() - transactionService.getMonthlyExpenses()) /
                            transactionService.getMonthlyIncome() * 100));
            dashboard.put("analytics", analytics);

            dashboard.put("served_by", "WEB_BFF");
            return dashboard;
        }
    }

    // =============================================
    // 4. MOBILE BFF — Compact mobile data
    // =============================================

    static class MobileBFF {
        private AccountService accountService;
        private TransactionService transactionService;

        MobileBFF(AccountService as, TransactionService ts) {
            this.accountService = as;
            this.transactionService = ts;
        }

        /** Returns compact summary for mobile app */
        Map<String, Object> getDashboard() {
            Map<String, Object> dashboard = new LinkedHashMap<>();

            // Compact balance summary (just names and balances)
            List<Map<String, String>> balances = new ArrayList<>();
            for (Account acc : accountService.getAllAccounts()) {
                Map<String, String> summary = new LinkedHashMap<>();
                summary.put("name", acc.name);
                summary.put("balance", String.format("$%.2f", acc.balance));
                balances.add(summary);
            }
            dashboard.put("balances", balances);
            dashboard.put("total", String.format("$%.2f", accountService.getTotalBalance()));

            // Only last 5 transactions (mobile screen is small)
            List<Transaction> allTxns = transactionService.getAll();
            int limit = Math.min(5, allTxns.size());
            List<Map<String, String>> recentTxns = new ArrayList<>();
            for (int i = 0; i < limit; i++) {
                Transaction t = allTxns.get(i);
                Map<String, String> txn = new LinkedHashMap<>();
                txn.put("desc", t.description.length() > 20 ? t.description.substring(0, 20) + "…" : t.description);
                txn.put("amount", String.format("$%.2f", t.amount));
                txn.put("date", t.date);
                recentTxns.add(txn);
            }
            dashboard.put("recent_transactions", recentTxns);

            // Quick actions for mobile
            dashboard.put("quick_actions", Arrays.asList("Transfer", "Pay Bills", "Deposit"));
            dashboard.put("push_notification_token", "fcm-token-abc123");

            dashboard.put("served_by", "MOBILE_BFF");
            return dashboard;
        }
    }

    // =============================================
    // MAIN
    // =============================================

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║   BFF PATTERN DEMO — Banking Application                ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝");

        // Shared core services
        AccountService accountService = new AccountService();
        TransactionService transactionService = new TransactionService();

        // Separate BFFs
        WebBFF webBff = new WebBFF(accountService, transactionService);
        MobileBFF mobileBff = new MobileBFF(accountService, transactionService);

        // ---- Web Dashboard Response ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("WEB BFF — Rich Dashboard Response");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        Map<String, Object> webResponse = webBff.getDashboard();
        printResponse(webResponse, "  ");
        String webJson = webResponse.toString();
        System.out.println("\n  📊 Web response size: ~" + webJson.length() + " characters");

        // ---- Mobile App Response ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("MOBILE BFF — Compact App Response");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        Map<String, Object> mobileResponse = mobileBff.getDashboard();
        printResponse(mobileResponse, "  ");
        String mobileJson = mobileResponse.toString();
        System.out.println("\n  📱 Mobile response size: ~" + mobileJson.length() + " characters");

        // ---- Comparison ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("COMPARISON");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.printf("  Web BFF response:    ~%d chars | Full history | Analytics%n", webJson.length());
        System.out.printf("  Mobile BFF response: ~%d chars | Last 5 txns  | Quick actions%n", mobileJson.length());
        System.out.printf("  Size reduction:      ~%.0f%% smaller for mobile%n",
                (1.0 - (double) mobileJson.length() / webJson.length()) * 100);

        System.out.println("\n✅ Demo complete! The BFF Pattern provided:");
        System.out.println("   • Web dashboard gets rich data with analytics charts");
        System.out.println("   • Mobile app gets compact data optimized for small screens");
        System.out.println("   • Both share the same core Account & Transaction services");
        System.out.println("   • Each BFF can evolve independently");
    }

    @SuppressWarnings("unchecked")
    static void printResponse(Map<String, Object> map, String indent) {
        for (Map.Entry<String, Object> entry : map.entrySet()) {
            if (entry.getValue() instanceof Map) {
                System.out.println(indent + entry.getKey() + ":");
                printResponse((Map<String, Object>) entry.getValue(), indent + "  ");
            } else if (entry.getValue() instanceof List) {
                System.out.println(indent + entry.getKey() + ": " + entry.getValue());
            } else {
                System.out.println(indent + entry.getKey() + ": " + entry.getValue());
            }
        }
    }
}
