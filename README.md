# ServerSeed

## Description
- python/flask
- web/vue.js
- php/lumen
- go
- db/mysql
の構築済み環境
```
.
├── README.md
├── db/
├── web/
├── go/
├── php/
├── python_api/
└── docker-compose.yml
```
# Instllation
それぞれ how to setup (すぐ忘れるのでメモ) <br>
phpでエラーが出たらapt-get ~、vueでエラーが出たらexecしてnpm install ~
### db
- Dockerfile
- my.cnf
### php
- Dockerfile
- docker build ./php -t php-composer
- docker run -it -v ${PWD}/php:/php -w /php --rm php-composer composer install
- composer create-project --prefer-dist laravel/lumen ./php/
### vue.js
- Dockerfile
- vue create web/
- sudo rm -rf web/.git
### golang
- Dockerfile
- go.mod
### python
- Dockerfile
- requirements.txt

# Usage
必要のないものは rm -rf して、docker-compose からも消して使います<br>
使用時には ServerSeed とは別でリポジトリを作成して remote add しましょう<br>
1. git clone
2. rename
3. rm -rf .git
4. npm install
5. docker build ./php -t php-composer
6. docker run -it -v ${PWD}/php:/php -w /php --rm php-composer composer install

# Author 
@Cl2_CHINO