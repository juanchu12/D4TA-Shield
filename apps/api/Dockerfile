FROM php:8.4-cli-bookworm

# No intl: compiling it blows disk on small VMs and Shield doesn't need it.
RUN apt-get update && apt-get install -y --no-install-recommends \
        git unzip libpq-dev libzip-dev libsqlite3-dev curl \
    && docker-php-ext-install -j$(nproc) pdo_pgsql pdo_sqlite zip opcache \
    && rm -rf /var/lib/apt/lists/*

COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /app

COPY composer.json composer.lock* ./
RUN composer install --no-dev --no-scripts --no-autoloader --prefer-dist --ignore-platform-reqs

COPY . .
RUN composer dump-autoload --optimize --classmap-authoritative \
    && mkdir -p var/storage var/cache var/log config/jwt \
    && chown -R www-data:www-data var || true

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD curl -f http://127.0.0.1:8000/api/health || exit 1

CMD ["php", "-S", "0.0.0.0:8000", "-t", "public"]
