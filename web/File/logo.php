<?php
// logo.php — LFI-style logo loader challenge
// Only this script should be able to read /var/www/flag.txt

$baseDir  = __DIR__ . '/assets/images/';
$rawQuery = isset($_SERVER['QUERY_STRING']) ? $_SERVER['QUERY_STRING'] : '';

// Decoded "path" parameter
$path = isset($_GET['path']) ? $_GET['path'] : 'rcsc-logo';

// Did the attacker try a "%00" (null-byte style) bypass?
$hasNullBypass = (strpos($rawQuery, '%00') !== false);

// 1) If someone targets flag.txt but does NOT use %00 → block
if (strpos($path, 'flag.txt') !== false && !$hasNullBypass) {
    die('You cannot access flag.txt directly.');
}

$fullPath = null;

// 2) If they target flag.txt AND used %00 → treat as bypass and read secret flag
if (strpos($path, 'flag.txt') !== false && $hasNullBypass) {
    // Flag is OUTSIDE webroot: /var/www/flag.txt
    $fullPath = realpath('/var/www/flag.txt');

} else {
    // 3) Normal logo loading with weak "sanitization"

    // Strip simple traversal sequences (looks secure but isn't perfect)
    $safePath = str_replace(['../', '..\\'], '', $path);

    // Always force .png
    if (substr($safePath, -4) !== '.png') {
        $safePath .= '.png';
    }

    $fullPath = realpath($baseDir . '/' . $safePath);
}

// 4) If no valid file found → 404-style message
if (!$fullPath || !file_exists($fullPath)) {
    header('HTTP/1.0 404 Not Found');
    echo 'Logo resource not found.';
    exit;
}

// 5) Always pretend it's an image, even if it's flag.txt
header('Content-Type: image/png');
readfile($fullPath);
