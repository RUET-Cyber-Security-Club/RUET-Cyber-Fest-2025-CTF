<?php
// db.php
$db_path = __DIR__ . '/database.sqlite';
$db = new SQLite3($db_path);

// Create tables if not exist
$db->exec('CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)');

$db->exec('CREATE TABLE IF NOT EXISTS posts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL
)');

// Seed admin user (flag as password)
$res = $db->querySingle('SELECT COUNT(*) FROM users');
if ($res == 0) {
    // FLAG – customize however you like
    $flag = 'RCSC{bl1nd_sqli_brut3f0rc3}';
    $stmt = $db->prepare('INSERT INTO users (username, password) VALUES (:u, :p)');
    $stmt->bindValue(':u', 'admin', SQLITE3_TEXT);
    $stmt->bindValue(':p', $flag, SQLITE3_TEXT);
    $stmt->execute();
}

// Seed some event-themed blog posts
$resPosts = $db->querySingle('SELECT COUNT(*) FROM posts');
if ($resPosts == 0) {
    $posts = [
        [
            'RCSC Cyber Fest 2025 Announcement',
            'RCSC Cyber Fest 2025 is a two-day national cybersecurity event at RUET featuring CTF, workshops, talks and networking.'
        ],
        [
            'RUET: Campus & Academic Excellence',
            'Rajshahi University of Engineering & Technology (RUET) is known for its strong engineering programs, active student clubs, and a growing focus on research, innovation, and technology-driven initiatives across the campus.'
        ],
        [
            'RUET Cyber Security Club (RCSC)',
            'RCSC is organizing Cyber Fest 2025 to bring together students, professionals and researchers to strengthen Bangladesh’s cybersecurity ecosystem.'
        ],
        [
            'Admin Portal & Event Registration',
            'The internal admin portal manages Cyber Fest registrations, schedules and scoreboards. It is supposed to be secure—but developers sometimes make mistakes.'
        ]
    ];

    $stmt = $db->prepare('INSERT INTO posts (title, description) VALUES (:t, :d)');
    foreach ($posts as $p) {
        $stmt->bindValue(':t', $p[0], SQLITE3_TEXT);
        $stmt->bindValue(':d', $p[1], SQLITE3_TEXT);
        $stmt->execute();
    }
}
