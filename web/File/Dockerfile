FROM php:5.6-apache

# Webroot
WORKDIR /var/www/html

# Copy the whole web app into the web root
COPY . /var/www/html

# Copy the real flag OUTSIDE the web root
# => Inside the container this creates /var/www/flag.txt
COPY S0m3_secret_flag.txt /var/www/flag.txt

# (Optional) enable error display for debugging
RUN echo "display_errors=On" >> /usr/local/etc/php/php.ini \
    && echo "error_reporting=E_ALL" >> /usr/local/etc/php/php.ini
