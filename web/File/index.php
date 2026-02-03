<?php
// index.php
?>
<!DOCTYPE html>
<html lang="en">
<head>
    <?php include __DIR__ . '/includes/header.php'; ?>
</head>
<body>
    <?php include __DIR__ . '/includes/navbar.php'; ?>

    <main class="container">
        <?php
        $page = isset($_GET['page']) ? $_GET['page'] : 'home';

        // Simple whitelist to keep the main router safe
        $allowed_pages = [
            'home'        => 'home.php',
            'about'       => 'about.php',
            'description' => 'description.php',
            'contact'     => 'contact.php'
        ];

        if (array_key_exists($page, $allowed_pages)) {
            include __DIR__ . '/pages/' . $allowed_pages[$page];
        } else {
            echo '<h2>404 – Page Not Found</h2>';
            echo '<p>The page you are looking for does not exist.</p>';
        }
        ?>
    </main>

    <?php include __DIR__ . '/includes/footer.php'; ?>
</body>
</html>
