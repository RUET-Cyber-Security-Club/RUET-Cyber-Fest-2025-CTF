<?php
// admin/index.php
session_start();
require_once __DIR__ . '/../db.php';

// Auth check BEFORE any HTML output
if (!isset($_SESSION['admin_logged_in']) || $_SESSION['admin_logged_in'] !== true) {
    header('Location: /admin/login.php');
    exit;
}

include __DIR__ . '/../header.php';
?>
<h1>Cyber Fest Admin Panel</h1>
<p>
    Internal panel for managing RCSC Cyber Fest 2025 registrations, schedules, and scoreboards.
</p>
<p>
    There is nothing interesting left here for you as a CTF player – the important part was
    the <strong>password you used to log in</strong>.
</p>
<p><a href="/admin/logout.php">Logout</a></p>
<?php
include __DIR__ . '/../footer.php';
