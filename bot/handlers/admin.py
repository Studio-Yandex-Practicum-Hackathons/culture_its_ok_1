from datetime import datetime

from aiogoogle import excs
from aiogram import F, Router, types
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm import context
from core.config import settings
from core.logger import log_exceptions, logger_factory
from core.states import Admin
from core.utils import (check_is_email, date_str_to_datetime,
                        delete_inline_keyboard, delete_keyboard,
                        send_message_and_sleep)
from db.crud import route_crud
from keyboards.inline import get_inline_keyboard
from services.report import REPORT_TYPES, ReportType
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logger_factory(__name__)

# ----------------------
ENTER_INSTRUCTION = ('Для доступа в административную зону введите команду:\n'
                     '/admin <i>ваш_пароль</i>')
WRONG_PASSWORD = 'Неверный пароль'
ADMIN_WELCOME = ('Добро пожаловать в административную зону. Для выхода из '
                 'неё, введите команду /exit')
ADMIN_EXIT_CONFIRMATION = 'Вы покинули административную зону'
SELECT_REPORT = 'Выберите вид отчёта, который желаете получить.'
SELECT_ROUTE = 'Выберите маршрут, по которому вы желаете получить отчёт.'
ENTER_PERIOD = ('Введите период, за который вы желаете получить отчёт.\n'
                'Примеры запросов:\n'
                '<u>03.08.2023</u> - получить отчёт с указанной даты по '
                'настоящее время.\n'
                '<u>03.08.2023-12.08.2023</u> - получить отчёт за указанный '
                'диапазон')
BAD_DATE_FORMAT = 'Неверный формат даты.'
BAD_PERIOD_RANGE = 'Дата начала не может быть позже сегодняшнего дня.'
ENTER_EMAIL = ('Введите адрес электронной почты, которому будет предоставлен '
               'доступ к отчёту.')
BAD_EMAIL = 'Неверный формат адреса электронной почты.'
REPORT_PREPARING = ('Отчёт готовится. Пожалуйста, подождите. В некоторых '
                    'случаях, это может занимать до нескольких минут.')
REPORT_ERROR = 'Ошибка при создании Google-таблицы. Попробуйте ещё раз.'
REPORT_READY = 'Отчёт сформирован. Для доступа к нему перейдите по ссылке:'
# ----------------------


@router.message(Command('admin'))
@log_exceptions(logger)
async def cmd_admin(
        message: types.Message,
        state: context.FSMContext,
        command: CommandObject
):
    await state.clear()

    if command.args is None:
        await message.answer(
            ENTER_INSTRUCTION,
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    if command.args != settings.bot.admin_password.get_secret_value():
        await message.answer(
            WRONG_PASSWORD,
            reply_markup=types.ReplyKeyboardRemove()
        )
        return

    # === точка входа в административную зону ===
    await message.delete()
    await delete_keyboard(message)
    await send_message_and_sleep(message, ADMIN_WELCOME)
    await admin_welcome(message, state)


@router.message(Command('exit'))
@log_exceptions(logger)
async def cmd_exit(
        message: types.Message,
        state: context.FSMContext
):
    await state.clear()
    await message.answer(ADMIN_EXIT_CONFIRMATION,
                         reply_markup=types.ReplyKeyboardRemove())


@log_exceptions(logger)
async def admin_welcome(
        message: types.Message,
        state: context.FSMContext,
):
    reports = {
        report['name']: f'report${report_id}'
        for report_id, report in REPORT_TYPES.items()
    }
    await message.answer(
        SELECT_REPORT,
        reply_markup=get_inline_keyboard(reports, adjust=1)
    )
    await state.set_state(Admin.report_selection)


@router.callback_query(Admin.report_selection, F.data.startswith('report$'))
@log_exceptions(logger)
async def report_selection(
        callback: types.CallbackQuery,
        state: context.FSMContext,
        session: AsyncSession
):
    report_id = int(callback.data.split("$")[1])

    if report_id in REPORT_TYPES:
        await delete_inline_keyboard(callback.message)
        await state.update_data({'report_id': report_id})

        if report_id == ReportType.REFLECTION_REPORT:
            await route_selection(callback, state, session)
        elif report_id == ReportType.USERS_REPORT:
            await email_input(callback.message, state, session)
        else:
            await period_selection(callback.message, state, session)


@router.callback_query(Admin.route_selection, F.data.startswith('rpt_route$'))
@log_exceptions(logger)
async def route_selection(
        callback: types.CallbackQuery,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != Admin.route_selection:
        routes = {
            route.name: f'rpt_route${route.id}' for route in
            await route_crud.get_all(session, sort='id asc')
        }
        await callback.message.answer(
            SELECT_ROUTE,
            reply_markup=get_inline_keyboard(routes, adjust=1)
        )
        await state.set_state(Admin.route_selection)
        return

    route_id = int(callback.data.split("$")[1])

    route_ids = [
        route.id for route in
        await route_crud.get_all(session, sort='id asc')
    ]

    if route_id in route_ids:
        await delete_inline_keyboard(callback.message)
        await state.update_data({'route_id': route_id})
        await period_selection(callback.message, state, session)


@router.message(Admin.period_selection, F.text)
@log_exceptions(logger)
async def period_selection(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != Admin.period_selection:
        await message.answer(ENTER_PERIOD)
        await state.set_state(Admin.period_selection)
        return

    try:
        start, end = (value.strip() for value in message.text.split('-'))
    except ValueError:
        start, end = message.text.strip(), datetime.now().strftime('%d.%m.%Y')

    try:
        start, end = [date_str_to_datetime(date) for date in (start, end)]
    except (ValueError, TypeError):
        await send_message_and_sleep(message, BAD_DATE_FORMAT)
        await message.answer(ENTER_PERIOD)
        return

    if start > end:
        await message.answer(BAD_PERIOD_RANGE)
        return

    await state.update_data({
        'start': start.strftime('%d.%m.%Y'),
        'end': end.strftime('%d.%m.%Y')
    })
    await email_input(message, state, session)


@router.message(Admin.email_input, F.text)
@log_exceptions(logger)
async def email_input(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if await state.get_state() != Admin.email_input:
        await message.answer(ENTER_EMAIL)
        await state.set_state(Admin.email_input)
        return

    if not check_is_email(message.text):
        await message.answer(BAD_EMAIL)
        return

    await state.update_data({'email': message.text})
    state_data = await state.get_data()

    await message.answer(REPORT_PREPARING)

    try:
        report_url = await REPORT_TYPES[state_data['report_id']]['handler'](
            session, **state_data
        )
        await message.answer(REPORT_READY)
        await send_message_and_sleep(message, report_url, 3)
    except excs.HTTPError:
        await send_message_and_sleep(message, REPORT_ERROR, 3)

    await state.clear()
    await admin_welcome(message, state)
