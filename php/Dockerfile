FROM php:8.0

RUN apt-get update && apt-get install -y git

WORKDIR root

RUN docker-php-ext-install pdo_mysql

# composerのinstall
RUN curl -O https://getcomposer.org/download/2.1.5/composer.phar && \
    php -r "if (hash_file('sha256', 'composer.phar') === '55ce33d7678c5a611085589f1f3ddf8b3c52d662cd01d4ba75c0ee0459970c2200a51f492d557530c71c15d8dba01eae') { echo 'Installer verified'; } else { echo 'Installer corrupt'; unlink('composer-setup.php'); } echo PHP_EOL;" && \
    mv ./composer.phar $(dirname $(which php))/composer && \
    chmod 777 $(dirname $(which php))/composer
