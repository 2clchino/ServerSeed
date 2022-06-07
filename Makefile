.PHONY: start

setup:
	docker build ./php -t php-composer
	docker run -it -v ${PWD}/php:/php -w /php --rm php-composer composer install
	docker-compose -f docker-compose.yml build
	cd web
	npm install

migrate:
	docker-compose up -d db php
	docker-compose exec php php artisan migrate

start:
	docker-compose -f docker-compose.yml up -d

stop:
	docker-compose down