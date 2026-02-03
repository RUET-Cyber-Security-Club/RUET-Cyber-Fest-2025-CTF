<?php
// admin/login.php
session_start();
require_once __DIR__ . '/../db.php';

$error = '';

// Handle login BEFORE output
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $user = isset($_POST['username']) ? $_POST['username'] : '';
    $pass = isset($_POST['password']) ? $_POST['password'] : '';

    // SAFE: prepared statement (no SQLi here)
    $stmt = $db->prepare('SELECT id FROM users WHERE username = :u AND password = :p');
    $stmt->bindValue(':u', $user, SQLITE3_TEXT);
    $stmt->bindValue(':p', $pass, SQLITE3_TEXT);
    $res = $stmt->execute();
    $row = $res->fetchArray(SQLITE3_ASSOC);

    if ($row) {
        $_SESSION['admin_logged_in'] = true;
        header('Location: /admin/');
        exit;
    } else {
        $error = 'Invalid credentials.';
    }
}

// Only now start HTML output
include __DIR__ . '/../header.php';
?>
<h1>RCSC Cyber Fest 2025 – Admin Login</h1>
<p>This login form is not vulnerable to SQL injection. The real bug is elsewhere…</p>

<?php if ($error): ?>
    <p style="color: #ff6666;"><?php echo htmlspecialchars($error); ?></p>
<?php endif; ?>

<form method="post">
    <label>Username</label>
    <input type="text" name="username" required>
    <label>Password</label>
    <input type="password" name="password" required>
    <input type="submit" value="Login">
</form>
<?php
include __DIR__ . '/../footer.php';
