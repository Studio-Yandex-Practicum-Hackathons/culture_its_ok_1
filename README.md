![Development](https://github.com/Studio-Yandex-Practicum-Hackathons/culture_its_ok_1/actions/workflows/dev_workflows.yml/badge.svg)
![Production](https://github.com/Studio-Yandex-Practicum-Hackathons/culture_its_ok_1/actions/workflows/prod_workflows.yml/badge.svg)

## **Стек технологий**:
![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
![image](https://img.shields.io/badge/sentry-purple?style=for-the-badge&logo=sentry)
![image](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![image](https://img.shields.io/badge/redis-CC0000.svg?&style=for-the-badge&logo=redis&logoColor=white)
![image](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
![image](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)

![image](https://img.shields.io/badge/sql%20alchemy-grey?style=for-the-badge&logo=alchemy)
![image](https://img.shields.io/badge/alembic-7FFFD4?style=for-the-badge)
![image](https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)
![image](	https://img.shields.io/badge/aiogram-018bff?style=for-the-badge&logo=aiogram&logoColor=white)
![image](https://img.shields.io/badge/pydantic-FF1493?style=for-the-badge&logo=pydantic)
![image](https://img.shields.io/badge/poetry-4169E1?style=for-the-badge&logo=poetry)

# **Бот АНО "Культура"**
Бот проводит экскурсии-медиации по местам с работами уличных художников в 
городе Ростов-на-Дону в реальном времени. На выбор несколько маршрутов. 
На протяжении всего маршрута бот "общается", описывает арт-объекты, рассказывает 
интересные факты о них, давая возможность порефлексировать.

<br>

Бот содержит административную зону, доступ к которой осуществляется по паролю 
и в которой можно сформировать следующие виды отчётов:

* Отчёт по пользователям (по всем пользователям в БД)
* Отчёт по маршрутам (за указанный период)
* Отчёт по рефлексии (по конкретному маршруту за указанный период)

Указав адрес электронной почты в ходе диалога с ботом, он возвращает ссылку на 
Google-таблицу с отчётом

<br>

Так же есть браузерная административная панель со следующими особенностями:

* Можно редактировать существующие маршруты или создавать новые, менять местами порядок отображения объектов
* Можно помечать маршруты или этапы неактивными на время их составления/редактирования или в случае, если какой-то маршрут пройти стало невозможно (например, работа была повреждена)
* Маршрутов может быть больше трёх, но пользователям выводятся первые три (неактивные не выводятся)
* Возможно редактировать текст на всех кнопках
* Загружаемые фотографии автоматически уменьшаются до указанного размера

___
## Как это работает:
* По команде `/start` бот предлагает ввести имя, возраст и хобби.
* Дальше предлагается выбрать маршрут, почитать описание и начать следовать по одному из них.
* В ходе прохождения маршрута, бот взаимодействует с пользователем, отправляя тексты, 
фоторграфии и предлагая порефлексировать (ответить на вопрос, отправив текстовое 
или голосовое сообщение), а также поучаствовать в викторине
* В конце маршрута предлагается оценить маршрут и заполнить форму обратной связи.
___
## **Как запустить проект**:

- Склонируйте репозитарий:
```
git clone git@github.com:Studio-Yandex-Practicum-Hackathons/culture_its_ok_1.git
```

- Установите Docker согласно инструкции с официального сайта: _https://docs.docker.com/_
- Получите все необходимые данные для переменных окружения: `telegram токен`, 
`sentry dsn`, `info сервисного аккаунта Google`, `сслыку на форму опроса для web app` (например, Google Forms. В целях пробного запуска можно указать любой URL)`


- В папке infra/ создайте папку env с файлами переменных окружения (в качестве примера
можно взять папку env.examle):

```
# env/.general

# Server
SERVER_HOST=<ip адрес или доменное имя сервера>
SERVER_PORT=80

# Versions
POSTGRES_VERSION=15
REDIS_VERSION=7.0.8
NGINX_VERSION=1.23.3

# Hosts
POSTGRES_HOST=postgres
REDIS_HOST=redis
DJANGO_HOST=django
NGINX_HOST=nginx

# Ports
POSTGRES_PORT=5432
REDIS_PORT=6379
DJANGO_PORT=8000
```
```
# env/.bot

TELEGRAM_TOKEN=<...>
DEBUG=FALSE
ADMIN_PASSWORD=password     # пароль от административной зоны
READING_SPEED=250           # скорость чтения текста (слов в минуту)
PHOTO_SHOW_DELAY=5          # задержка при показе фотографий (секунд)
REFLECTION_TEXT_LIMIT=500   # предельная длина текста рефлексии (символов)
REFLECTION_VOICE_LIMIT=120  # предельная длина голосового сообщения рефлексии (секунд)
SURVEY_URL=<...>            # ссылка на страницу опроса для отображения в web app
```
```
# env/.django

ALLOWED_HOSTS=127.0.0.1,<ip адрес или доменное имя сервера>
SECRET_KEY=<...>
DEBUG=False
PHOTO_RESIZE_QUALITY=medium  # качество сжатия картинок, загружаемых через админку (low/medium/high)
```
```
# env.google

TYPE=service_account
PROJECT_ID=<...>
PRIVATE_KEY_ID=<...>
PRIVATE_KEY=<...>
CLIENT_EMAIL=<...>
CLIENT_ID=<...>
AUTH_URI=https://accounts.google.com/o/oauth2/auth
TOKEN_URI=https://oauth2.googleapis.com/token
AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
CLIENT_X509_CERT_URL=HTTPS://WWW.GOOGLEAPIS.COM/ROBOT/V1/METADATA/X509/SERVICE-ACCOUNT%40CEDAR-CHANNEL-394314.IAM.GSERVICEACCOUNT.COM
UNIVERSE_DOMAIN=googleapis.com"
SPREADSHEET_URL="https://docs.google.com/spreadsheets/d/{}"
```
```
# env/.postgres

POSTGRES_DB=database
POSTGRES_USER=user
POSTGRES_PASSWORD=password
```
```
# env/.sentry

SENTRY_DSN=<...>
```

* Создайте и запустите docker контейнеры:

для запуска из образов с Docker Hub: 
```
# Linux
sudo docker compose --env-file=env/.general up --build -d

# Windows
docker compose --env-file=env/.general up --build -d
```
для локальной сборки контейнеров:
```
# Linux
sudo docker compose --file=docker-compose-dev.yaml --env-file=env/.general up --build -d

# Windows
docker compose --file=docker-compose-dev.yaml --env-file=env/.general up --build -d
```

* Создайте суперпользователя для входа в админку Django (пример для случая локальной сборки контенеров):
```
(sudo) docker compose --file=docker-compose-dev.yaml --env-file=env/.general exec bash django

python manage.py createsuperuser
```
Админка будет доступна по адресу: _http://<ip адрес сервера>/admin/_

## **Как наполнить базу**:

* Из директории `/infra/data` скопируйте файл `routes.json` и папку `media` в контейнер Django:
```
(sudo) docker compose --file=docker-compose-dev.yaml --env-file=env/.general cp data/routes.json django:/app/

(sudo) docker compose --file=docker-compose-dev.yaml --env-file=env/.general cp data/media django:/app/
```
* Зайдите в контейнер Django под пользователем root и поменяйте права на папку `media`
```
(sudo) docker compose --file=docker-compose-dev.yaml --env-file=env/.general exec -u root django bash

chown -R admin:admin media
```
* Залейте дамп в базу данных:
```
python manage.py loaddata routes.json
```
___

## **Разработчики**:
[Александр Бондаренко](https://github.com/dcomrad) - Тимлид

[Александр Гусаров](https://github.com/GUSICATC) - Разработчик

[Даниил Ларюшин](https://github.com/danlaryushin) - Разработчик

[Полина Николаева](https://github.com/STI-xa) - Разработчик

[Сергей Ткачук](https://github.com/SergeychUK92) - Разработчик

[Ярослав Лошкарев](https://github.com/94R1K) - Разработчик