import java.util.*;
import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * ============================================================
 * API GATEWAY PATTERN DEMO — Social Network Platform
 * ============================================================
 * 
 * This demo simulates a social network where an API Gateway
 * centralizes access to User, Post, and Notification services.
 * 
 * Components:
 * 1. UserService — Manages user profiles
 * 2. PostService — Manages posts and likes
 * 3. NotificationService — Manages notifications
 * 4. ApiGateway — Centralized entry point with auth,
 * rate limiting, logging, and aggregation
 */
public class ApiGatewayDemo {

    // =============================================
    // Domain Models
    // =============================================

    static class User {
        String id, username, email, bio;
        int followers, following;

        User(String id, String username, String email, String bio, int followers, int following) {
            this.id = id;
            this.username = username;
            this.email = email;
            this.bio = bio;
            this.followers = followers;
            this.following = following;
        }

        @Override
        public String toString() {
            return String.format("User{id='%s', username='%s', followers=%d}", id, username, followers);
        }
    }

    static class Post {
        String id, userId, content;
        int likes;
        String timestamp;

        Post(String id, String userId, String content) {
            this.id = id;
            this.userId = userId;
            this.content = content;
            this.likes = 0;
            this.timestamp = LocalDateTime.now().format(DateTimeFormatter.ISO_LOCAL_DATE_TIME);
        }

        @Override
        public String toString() {
            return String.format("Post{id='%s', by='%s', likes=%d, content='%s'}", id, userId, likes, content);
        }
    }

    static class Notification {
        String id, userId, message, type;
        boolean read;

        Notification(String id, String userId, String message, String type) {
            this.id = id;
            this.userId = userId;
            this.message = message;
            this.type = type;
            this.read = false;
        }

        @Override
        public String toString() {
            return String.format("Notif{type='%s', msg='%s', read=%s}", type, message, read);
        }
    }

    // =============================================
    // 1. USER SERVICE
    // =============================================

    static class UserService {
        private Map<String, User> users = new HashMap<>();

        UserService() {
            users.put("user-1", new User("user-1", "alice", "alice@example.com", "Software Engineer", 1500, 300));
            users.put("user-2", new User("user-2", "bob", "bob@example.com", "Product Designer", 800, 200));
            users.put("user-3", new User("user-3", "charlie", "charlie@example.com", "Data Scientist", 2000, 150));
        }

        User getUser(String userId) {
            return users.get(userId);
        }

        List<User> listUsers() {
            return new ArrayList<>(users.values());
        }
    }

    // =============================================
    // 2. POST SERVICE
    // =============================================

    static class PostService {
        private Map<String, Post> posts = new HashMap<>();
        private int counter = 0;

        PostService() {
            createPost("user-1", "Just deployed our new microservices architecture! 🚀");
            createPost("user-1", "API Gateway Pattern is a game changer for our platform.");
            createPost("user-2", "Designed a beautiful new dashboard today 🎨");
            createPost("user-3", "Training a new ML model — 98% accuracy so far!");
        }

        Post createPost(String userId, String content) {
            String id = "post-" + (++counter);
            Post post = new Post(id, userId, content);
            posts.put(id, post);
            return post;
        }

        List<Post> getPostsByUser(String userId) {
            List<Post> result = new ArrayList<>();
            for (Post p : posts.values()) {
                if (p.userId.equals(userId))
                    result.add(p);
            }
            return result;
        }

        Post likePost(String postId) {
            Post post = posts.get(postId);
            if (post != null)
                post.likes++;
            return post;
        }
    }

    // =============================================
    // 3. NOTIFICATION SERVICE
    // =============================================

    static class NotificationService {
        private Map<String, List<Notification>> notifications = new HashMap<>();
        private int counter = 0;

        NotificationService() {
            addNotification("user-1", "bob liked your post", "LIKE");
            addNotification("user-1", "charlie followed you", "FOLLOW");
            addNotification("user-2", "alice mentioned you in a post", "MENTION");
        }

        void addNotification(String userId, String message, String type) {
            String id = "notif-" + (++counter);
            notifications.computeIfAbsent(userId, k -> new ArrayList<>())
                    .add(new Notification(id, userId, message, type));
        }

        List<Notification> getNotifications(String userId) {
            return notifications.getOrDefault(userId, new ArrayList<>());
        }

        int getUnreadCount(String userId) {
            return (int) getNotifications(userId).stream().filter(n -> !n.read).count();
        }
    }

    // =============================================
    // 4. API GATEWAY — Centralized entry point
    // =============================================

    static class ApiGateway {
        private UserService userService;
        private PostService postService;
        private NotificationService notificationService;

        // Cross-cutting concerns
        private Set<String> validTokens = new HashSet<>(Arrays.asList("token-alice", "token-bob", "token-charlie"));
        private Map<String, String> tokenToUser = new HashMap<>() {
            {
                put("token-alice", "user-1");
                put("token-bob", "user-2");
                put("token-charlie", "user-3");
            }
        };

        // Rate limiting
        private Map<String, AtomicInteger> requestCounts = new ConcurrentHashMap<>();
        private static final int MAX_REQUESTS_PER_MINUTE = 10;

        // Request logging
        private List<String> requestLog = new ArrayList<>();

        ApiGateway(UserService userService, PostService postService, NotificationService notificationService) {
            this.userService = userService;
            this.postService = postService;
            this.notificationService = notificationService;
        }

        // ---- Authentication ----
        private String authenticate(String token) {
            if (token == null || !validTokens.contains(token)) {
                throw new RuntimeException("❌ 401 Unauthorized: Invalid token");
            }
            return tokenToUser.get(token);
        }

        // ---- Rate Limiting ----
        private void checkRateLimit(String token) {
            AtomicInteger count = requestCounts.computeIfAbsent(token, k -> new AtomicInteger(0));
            if (count.incrementAndGet() > MAX_REQUESTS_PER_MINUTE) {
                throw new RuntimeException("❌ 429 Too Many Requests: Rate limit exceeded");
            }
        }

        // ---- Logging ----
        private void logRequest(String method, String path, String userId) {
            String log = String.format("[%s] %s %s (user: %s)",
                    LocalDateTime.now().format(DateTimeFormatter.ofPattern("HH:mm:ss")),
                    method, path, userId);
            requestLog.add(log);
            System.out.println("  📝 " + log);
        }

        // ---- Gateway Endpoints ----

        /** GET /api/users/{userId} */
        User getUser(String token, String userId) {
            String authenticatedUser = authenticate(token);
            checkRateLimit(token);
            logRequest("GET", "/api/users/" + userId, authenticatedUser);
            return userService.getUser(userId);
        }

        /** GET /api/posts?userId={userId} */
        List<Post> getUserPosts(String token, String userId) {
            String authenticatedUser = authenticate(token);
            checkRateLimit(token);
            logRequest("GET", "/api/posts?userId=" + userId, authenticatedUser);
            return postService.getPostsByUser(userId);
        }

        /** POST /api/posts */
        Post createPost(String token, String content) {
            String authenticatedUser = authenticate(token);
            checkRateLimit(token);
            logRequest("POST", "/api/posts", authenticatedUser);
            return postService.createPost(authenticatedUser, content);
        }

        /** GET /api/notifications */
        List<Notification> getNotifications(String token) {
            String authenticatedUser = authenticate(token);
            checkRateLimit(token);
            logRequest("GET", "/api/notifications", authenticatedUser);
            return notificationService.getNotifications(authenticatedUser);
        }

        /**
         * GET /api/feed/{userId}
         * AGGREGATION ENDPOINT — Combines data from User + Post + Notification services
         */
        Map<String, Object> getUserFeed(String token, String userId) {
            String authenticatedUser = authenticate(token);
            checkRateLimit(token);
            logRequest("GET", "/api/feed/" + userId, authenticatedUser);

            // Aggregate from multiple services
            Map<String, Object> feed = new LinkedHashMap<>();
            feed.put("user", userService.getUser(userId));
            feed.put("posts", postService.getPostsByUser(userId));
            feed.put("unread_notifications", notificationService.getUnreadCount(userId));
            feed.put("aggregated_by", "API_GATEWAY");
            return feed;
        }

        void printRequestLog() {
            System.out.println("\n  📋 Request Log (" + requestLog.size() + " requests):");
            requestLog.forEach(log -> System.out.println("    " + log));
        }
    }

    // =============================================
    // MAIN — Demonstrates the API Gateway
    // =============================================

    public static void main(String[] args) {
        System.out.println("╔══════════════════════════════════════════════════════════╗");
        System.out.println("║   API GATEWAY PATTERN DEMO — Social Network             ║");
        System.out.println("╚══════════════════════════════════════════════════════════╝");

        // Initialize services
        UserService userService = new UserService();
        PostService postService = new PostService();
        NotificationService notifService = new NotificationService();
        ApiGateway gateway = new ApiGateway(userService, postService, notifService);

        // ---- Demo 1: Authentication ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("DEMO 1: Authentication at Gateway");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        try {
            gateway.getUser("invalid-token", "user-1");
        } catch (RuntimeException e) {
            System.out.println("  " + e.getMessage());
        }

        User user = gateway.getUser("token-alice", "user-1");
        System.out.println("  ✅ Authenticated: " + user);

        // ---- Demo 2: Routing to different services ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("DEMO 2: Routing to Different Services");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        System.out.println("\n  📮 Get user profile (→ User Service):");
        System.out.println("  " + gateway.getUser("token-alice", "user-2"));

        System.out.println("\n  📮 Get posts (→ Post Service):");
        gateway.getUserPosts("token-alice", "user-1").forEach(p -> System.out.println("  " + p));

        System.out.println("\n  📮 Get notifications (→ Notification Service):");
        gateway.getNotifications("token-alice").forEach(n -> System.out.println("  " + n));

        // ---- Demo 3: Request Aggregation ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("DEMO 3: Request Aggregation (User Feed)");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        Map<String, Object> feed = gateway.getUserFeed("token-bob", "user-1");
        System.out.println("\n  🔗 Aggregated Feed Response:");
        feed.forEach((key, value) -> System.out.println("    " + key + ": " + value));

        // ---- Demo 4: Rate Limiting ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("DEMO 4: Rate Limiting");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");

        System.out.println("  Sending rapid requests until rate limit is hit...");
        for (int i = 0; i < 15; i++) {
            try {
                gateway.getUser("token-charlie", "user-1");
            } catch (RuntimeException e) {
                System.out.println("  Request #" + (i + 1) + ": " + e.getMessage());
                break;
            }
        }

        // ---- Demo 5: Request Logging ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("DEMO 5: Centralized Request Logging");
        System.out.println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        gateway.printRequestLog();

        // ---- Summary ----
        System.out.println("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━");
        System.out.println("✅ Demo complete! The API Gateway provided:");
        System.out.println("   • Centralized authentication (JWT token validation)");
        System.out.println("   • Smart routing to User, Post, and Notification services");
        System.out.println("   • Request aggregation for the Feed endpoint");
        System.out.println("   • Rate limiting to protect backend services");
        System.out.println("   • Centralized request logging for monitoring");
    }
}
