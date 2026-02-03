# Dockerfile
FROM php:8.2-apache

# For this CTF we don't need to compile extra PHP extensions manually.
# The base image already has what we need for a simple SQLite-based app
# (or you can switch later to PDO-only if you want).

# Copy app into web root
COPY . /var/www/html

# Permissions (for SQLite db file etc.)
RUN chown -R www-data:www-data /var/www/html
