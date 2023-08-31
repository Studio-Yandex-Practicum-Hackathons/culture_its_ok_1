# **Бот АНО "Культура"**
Бот-медиатор, проводит экскурсии-медитации по местам с работами уличных художников в городе Ростов-на-Дону в реальном времени. На выбор несколько маршрутов. На протяжении всего маршрута бот "общается", описывает арт-объекты, рассказывает интересные факты о них, давая возможность порефлексировать.
В боте реализована административная панель, где можно создавать отчеты по маршрутам и пользователям. И так же есть браузерная административная панель, где можно конструировать и настраивать маршруты, как новые, так и старые.
___
## Как это работает:
* По команде `/start` бот приветствует вас и предлагает ввести имя, возраст и интересы.
* Дальше предлагается выбрать маршрут.
* После выбора маршрута, бот присылает описание и карту маршрута, указывает адрес начала маршрута, ссылка на адрес активна и открывается в Яндекс.картах.
* Попадая по адресу очередного арт-объекта, бот дает его описание, иногда задает вопросы об объектах, в ответ можно вводить как текстовые, так и голосовые сообщения.
* В конце маршрута предлагается оценить маршрут и есть форма обратной связи.
___
## **Как запустить проект**:

* Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:Studio-Yandex-Practicum-Hackathons/culture_its_ok_1.git
```

* Активировать виртуальное окружение и установить зависимости:
```
poetry shell
poetry install
```

* В корне папки `/infra` создать папку `/env` и наполнить файлы переменными окружения. Образец находится в `/infra/env.example`.


* Создать и запустить docker контейнеры:

*Linux:*
```
sudo docker compose --file=docker-compose-dev.yaml --env-file=env/.general up --build -d
```

*Windows:*
```
docker compose --file=docker-compose-dev.yaml --env-file=env/.general up --build -d
```

* Применить миграции:
```
poetry run alembic upgrade head
```

* Создать файл `.env` с переменными окружения в корне папки `/bot`. Пример наполнения файла находится в `/bot/.env.example`.

* Запустить проект:
```
poetry run python main.py
```

* Создать супер пользователя для входа в админку Django:
```
python manage.py createsuperuser
```


## **Как наполнить базу**:

* Из директории `/infra/data` скопировать файл `routes.json` и папку `media` в контейнер Django:
```
sudo docker compose --file=docker-compose-dev.yaml --env-file=env/.general cp data/routes.json django:/app/
```
```
sudo docker compose --file=docker-compose-dev.yaml --env-file=env/.general cp data/media django:/app/
```
* Зайти в контейнер Django под пользоватлеем root и поменять права на папку `media`
```
sudo docker compose --file=docker-compose-dev.yaml --env-file=env/.general exec -u root django bash
```
```
python manage.py loaddata routes.json
```
```
chown -R admin:admin media
```


___
## **Стэк технологий**:
* ![image](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)
* ![image](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)
* ![image](https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white)
* ![image](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)
* ![image](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
* ![image](	https://img.shields.io/badge/aiogram-018bff?style=for-the-badge&logo=aiogram&logoColor=white)
* ![image](https://img.shields.io/badge/redis-CC0000.svg?&style=for-the-badge&logo=redis&logoColor=white)
* ![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
* ![image](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)
* ![image](https://img.shields.io/badge/Google%20Sheets-34A853?style=for-the-badge&logo=google-sheets&logoColor=white)
* ![image](https://img.shields.io/badge/sentry-purple?style=for-the-badge&logo=sentry)
* ![image](https://img.shields.io/badge/alembic-7FFFD4?style=for-the-badge)
* ![image](https://img.shields.io/badge/sql%20alchemy-grey?style=for-the-badge&logo=alchemy)
* ![image](https://img.shields.io/badge/pydantic-FF1493?style=for-the-badge&logo=pydantic)
* ![image](https://img.shields.io/badge/poetry-4169E1?style=for-the-badge&logo=poetry)
___
## **Разработчики**:
[Александр Бондаренко](https://github.com/dcomrad) - Тимлид

[Александр Гусаров](https://github.com/GUSICATC) - Разработчик

[Даниил Ларюшин](https://github.com/danlaryushin) - Разработчик

[Полина Николаева](https://github.com/STI-xa) - Разработчик

[Сергей Ткачук](https://github.com/SergeychUK92) - Разработчик

[Ярослав Лошкарев](https://github.com/94R1K) - Разработчик

___