<?php
// index.php
require_once __DIR__ . '/db.php';
include __DIR__ . '/header.php';
?>
<h1>RCSC Cyber Fest 2025 – Web Challenge</h1>

<p>
    Welcome to the <strong>RCSC Cyber Fest 2025</strong> web-based challenge hosted by
    the <strong>RUET Cyber Security Club (RCSC)</strong>.
</p>

<p>
    This mini site represents a simple event blog created for Cyber Fest 2025. Somewhere in the system,
    the <strong>admin password</strong> (also your <strong>flag</strong>) is securely stored in the backend.
</p>

<ul>
    <li>Explore the <strong>Blog</strong> page – it includes a functional search feature.</li>
    <li>There is an <strong>Admin</strong> area at <code>/admin</code>, designed to resemble a real event management panel.</li>
    <li>Your goal is to uncover the admin password by observing the system's responses and understanding how typical RUET student-made applications behave.</li>
</ul>

<p>
    Good luck, and enjoy the challenge at RCSC Cyber Fest 2025!
</p>

<?php
include __DIR__ . '/footer.php';
?>
