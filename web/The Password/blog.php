<?php
// blog.php
require_once __DIR__ . '/db.php';
include __DIR__ . '/header.php';

$q = isset($_GET['q']) ? $_GET['q'] : '';
?>
<h1>RCSC Cyber Fest Blog</h1>
<p>
    Welcome to the official blog for <strong>RCSC Cyber Fest 2025</strong>.  
    Here you can explore posts, updates, and highlights from the event.  
    The search feature below is intentionally unstable for the challenge —  
    observe how the results shift based on how you phrase your queries…
</p>

<form method="get">
    <input type="text" name="q" placeholder="Search description..." value="<?php echo htmlspecialchars($q); ?>">
    <input type="submit" value="Search">
</form>
<hr>
<?php
if ($q === '') {
    // Default: show first 3 posts
    $sql = "SELECT id, title, description FROM posts LIMIT 3";
} else {
    // VULNERABLE: q is injected directly into the SQL
    $sql = "SELECT id, title, description FROM posts WHERE description LIKE '%$q%' LIMIT 3";
}

// Run query, but don't crash if SQL is invalid
$result = @$db->query($sql);  // @ to suppress warning for CTF
$count  = 0;

if ($result instanceof SQLite3Result) {
    while ($row = $result->fetchArray(SQLITE3_ASSOC)) {
        $count++;
        echo '<div class="blog-post">';
        echo '<h3>' . htmlspecialchars($row['title']) . '</h3>';
        echo '<p>' . htmlspecialchars($row['description']) . '</p>';
        echo '</div>';
    }
}

echo "<p><strong>Total posts shown:</strong> " . $count . "</p>";

include __DIR__ . '/footer.php';
