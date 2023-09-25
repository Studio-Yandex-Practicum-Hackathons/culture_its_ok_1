from collections import defaultdict
from datetime import datetime, timedelta
from enum import IntEnum

from core.config import settings
from core.utils import calc_avg, date_str_to_datetime
from db.crud import progress_crud, reflection_crud, route_crud, user_crud
from services.google_report import GoogleReport
from sqlalchemy.ext.asyncio import AsyncSession

VOICE_URL = f'http://{settings.server.host}:{settings.server.port}/media/voice/'  # noqa: E501

TITLE_TEMPLATE = 'Отчёт по {} бота арт-медиации АНО "Культура"'


class ReportType(IntEnum):
    USERS_REPORT = 1
    ROUTES_REPORT = 2
    REFLECTION_REPORT = 3


async def make_users_report(
        session: AsyncSession,
        email: str,
        **kwargs
) -> str:
    """
    Формирует отчёт по пользователям в виде Google-таблицы, предоставляя доступ
    заданному email.
    :return: URL на сформированный отчёт
    """
    users = await user_crud.get_all(session, sort='name asc')
    rows = []
    total_used_amount = 0
    for user in users:
        used_amount = await progress_crud.get_usage_count(user.id, session)
        rows.extend([
             [user.name, user.age, user.hobbies, used_amount]
        ])
        total_used_amount += used_amount

    title = TITLE_TEMPLATE.format('пользователям')
    header = [
        [title],
        [],
        ['Общее количество запусков бота', '', '', total_used_amount],
        [],
        ['Имя', 'Возраст', 'Интересы', 'Сколько раз воспользовались ботом']
    ]

    report = GoogleReport()
    report.set_title(f'{title} от {datetime.now().strftime("%d.%m.%Y")}')
    report.set_header(header)
    report.add_rows(rows)
    report.set_email(email)
    return await report.create()


async def make_routes_report(
        session: AsyncSession,
        start: str,
        end: str,
        email: str,
        **kwargs
) -> str:
    """
    Формирует отчёт по пользователям за заданный период [start, end] в виде
    Google-таблицы, предоставляя доступ заданному email.
    :return: URL на сформированный отчёт
    """
    routes = await route_crud.get_all(session, sort='id asc')

    title = TITLE_TEMPLATE.format('маршрутам')
    header = [
        [title],
        [],
        [f'Период: {start} - {end}'],
        [],
        *([f'Маршрут {i}', route.name] for i, route in enumerate(routes, 1)),
        [],
        ['', *[f'Маршрут {i}' for i in range(1, 4)]]
    ]
    rows = [
        ['Количество запусков бота'],
        ['их них, полностью прошли маршрут'],
        ['Количество уникальных пользователей'],
        ['Среднее время прохождения маршрута, минут'],
        ['Средний балл (количество оценок)']
    ]

    for route in routes:
        progress = await progress_crud.get_all_by_route_and_date_range(
            route.id,
            date_str_to_datetime(start),
            date_str_to_datetime(end) + timedelta(days=1),
            session
        )

        finished = [p for p in progress if p.finished_at]
        finished_rate = round(len(finished) / len(progress) * 100, 0) if progress else 0  # noqa: E501
        unique_users = {p.user_id for p in progress}
        rates = [p.rating for p in progress if p.rating]
        route_running_m = [
            int((p.finished_at - p.started_at).total_seconds() / 60)
            for p in progress if p.finished_at
        ]

        rows[0].append(len(progress))
        rows[1].append(f'{len(finished)} ({finished_rate}%)')
        rows[2].append(len(unique_users))
        rows[3].append(calc_avg(route_running_m, 0))
        rows[4].append(f'{calc_avg(rates, 1)} ({len(rates)})')

    report = GoogleReport()
    report.set_title(f'{title} от {datetime.now().strftime("%d.%m.%Y")}')
    report.set_header(header)
    report.add_rows(rows)
    report.set_email(email)
    return await report.create()


async def make_reflection_report(
        session: AsyncSession,
        route_id: int,
        start: str,
        end: str,
        email: str,
        **kwargs
) -> str:
    """
    Формирует отчёт по пользователям для заданного route_id за заданный период
    [start, end] в виде Google-таблицы, предоставляя доступ заданному email.
    :return: URL на сформированный отчёт
    """
    route = await route_crud.get(route_id, session)

    title = TITLE_TEMPLATE.format('рефлексии')
    header = [
        [title],
        [],
        [f'Маршрут: {route.name}'],
        [],
        [f'Период: {start} - {end}'],
        [],
        ['Текстовый ответ пользователя', 'Голосовое сообщение пользователя'],
        [],
    ]
    rows = []

    for stage in route.stages:
        reflections = await reflection_crud.get_all_by_route_stage_and_range(
            route_id,
            stage.id,
            date_str_to_datetime(start),
            date_str_to_datetime(end) + timedelta(days=1),
            session
        )

        if not reflections:
            continue

        rows.extend([
            [stage.name]
        ])

        question_to_answers = defaultdict(list)
        for reflection in reflections:
            question_to_answers[reflection.question].append(
                [reflection.answer, reflection.voice]
            )

        for question, answers in question_to_answers.items():
            rows.extend([
                [],
                [f'Вопрос: {question}'],
                *[[answer[0], VOICE_URL + answer[1] if answer[1] else None]
                  for answer in answers],
            ])

        rows.extend([
            []
        ])

    report = GoogleReport()
    report.set_title(f'{title} от {datetime.now().strftime("%d.%m.%Y")}')
    report.set_header(header)
    report.add_rows(rows)
    report.set_email(email)
    return await report.create()


REPORT_TYPES = {
    ReportType.USERS_REPORT: dict(
        name='Отчёт по пользователям',
        handler=make_users_report
    ),
    ReportType.ROUTES_REPORT: dict(
        name='Отчёт по маршрутам',
        handler=make_routes_report
    ),
    ReportType.REFLECTION_REPORT: dict(
        name='Отчёт по рефлексии',
        handler=make_reflection_report
    )
}
