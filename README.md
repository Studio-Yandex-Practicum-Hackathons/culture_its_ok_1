# **Бот АНО "Культура”**
Бот-медиатор, проводит экскурсии-медитации по местам с работами уличных художников в городе Ростов-на-Дону в реальном времени. На выбор несколько маршрутов. На протяжении всего маршрута бот "общается", описывает арт-объекты, рассказывает интересные факты о них, давая возможность порефлексировать.
___
## Как это работает:
* По команде `/start` бот приветствует вас и предлагает ввести имя, возраст и интересы.
* Дальше предлагается выбрать маршрут.
* После выбора маршрута, бот присылает описание и карту маршрута, указывает адрес начала маршрута, ссылка на адрес активна и открывается в Яндекс.картах.
* Попадая по адресу очередного арт-объекта, бот дает его описание, иногда задает вопросы об объектах, в ответ можно вводить как текстовые, так и голосовые сообщения.
* В конце маршрута предлагается оценить маршрут.

___
## **Как запустить проект**:

* Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:STI-xa/infra_sp2.git

cd api_yamdb
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

* Создать файл `.env` с переменными окружения в корне папки `/bot`. Пример наполнения файла находится в `/bot/.env.example`.

* Запустить проект:
```
poetry run python main.py
```
___
## **Разработчики**:
[Александр Бондаренко](https://github.com/dcomrad)

[Александр Гусаров](https://github.com/GUSICATC)

[Даниил Ларюшин](https://github.com/danlaryushin)

[Полина Николаева](https://github.com/STI-xa)

[Сергей Ткачук](https://github.com/SergeychUK92)

[Ярослав Лошкарев](https://github.com/94R1K)
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
