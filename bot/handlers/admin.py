from datetime import datetime

from aiogram import F, Router, types
from aiogram.filters.command import Command, CommandObject
from aiogram.fsm import context
from core.config import settings
from core.logger import log_dec, logger_factory
from core.states import Admin
from core.utils import (check_is_email, delete_inline_keyboard,
                        send_message_and_sleep)
from db.crud import route_crud
from keyboards.inline import get_inline_keyboard
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()
logger = logger_factory(__name__)

REPORT_TYPES = {
    1: 'Сводный отчёт с рефлексией',
    2: 'Сводный отчёт без рефлексии'
}

ENTER_INSTRUCTION = ('Для доступа в административную зону введите команду:\n'
                     '/admin <i>ваш_пароль</i>')
WRONG_PASSWORD = 'Неверный пароль'
ADMIN_WELCOME = 'Добро пожаловать в административную зону.'
ADMIN_EXIT = 'Покинуть административную зону'
ADMIN_EXIT_CONFIRMATION = 'Вы покинули административную зону'
SELECT_ROUTE = ('Пожалуйста, выберите маршрут, по которому вы желаете '
                'получить отчёт.')
ENTER_REPORT_TYPE = 'Выберите тип отчёта'
ENTER_PERIOD = ('Введите период, за который вы желаете получить отчёт.\n'
                'Примеры запросов:\n'
                '<b>03.08.2023</b> - получить отчёт с 03.08.2023 по настоящее '
                'время.\n'
                '<b>03.08.2023-12.08.2023</b> - получить отчёт с 03.08.2023 '
                'по 12.08.2023.')
BAD_DATE_FORMAT = 'Неверный формат даты.'
BAD_PERIOD_RANGE = 'Дата начала не может быть позже сегодняшнего дня.'
ENTER_EMAIL = ('Введите адрес электронной почты Google аккаунта, которому '
               'будет предоставлен доступ к отчёту.')
BAD_EMAIL = 'Неверный формат адреса электронной почты.'
REPORT_PREPARING = ('Отчёт готовится. Пожалуйста, подождите. В некоторых '
                    'случаях, это может занимать до нескольких минут.')
REPORT_READY = 'Отчёт сформирован. Для доступа к нему перейдите по ссылке:'


@router.message(Command('admin'))
@log_dec(logger)
async def cmd_admin(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession,
        command: CommandObject
):

    if command.args is None:
        await message.answer(
            ENTER_INSTRUCTION, reply_markup=types.ReplyKeyboardRemove()
        )
        return

    if command.args != settings.bot.admin_password.get_secret_value():
        await message.answer(
            WRONG_PASSWORD, reply_markup=types.ReplyKeyboardRemove()
        )
        return

    # === точка входа в административную зону ===
    await message.delete()
    await send_message_and_sleep(message, ADMIN_WELCOME)
    await admin_welcome(message, state, session)


@log_dec(logger)
async def admin_welcome(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession,
):
    await state.set_state(Admin.route_selection)

    routes = {
        route.name: f'rpt_route${route.id}' for route in
        await route_crud.get_all(session, sort='id asc')
    }

    await message.answer(
        SELECT_ROUTE, reply_markup=get_inline_keyboard(
            {**routes, ADMIN_EXIT: 'quit'}, adjust=1
        )
    )


@router.callback_query(Admin.route_selection, F.data.startswith('rpt_route$'))
@log_dec(logger)
async def route_selection(
        callback: types.CallbackQuery,
        state: context.FSMContext,
        session: AsyncSession
):
    route_id = int(callback.data.split("$")[1])

    route_ids = [
        route.id for route in
        await route_crud.get_all(session, sort='id asc')
    ]

    if route_id in route_ids:
        await state.set_data({'route_id': route_id})

        reports = {
            report_name: f'report${report_id}'
            for report_id, report_name in REPORT_TYPES.items()
        }
        await delete_inline_keyboard(callback.message)
        await callback.message.answer(
            ENTER_REPORT_TYPE,
            reply_markup=get_inline_keyboard(reports, adjust=1)
        )
        await state.set_state(Admin.report_selection)


@router.callback_query(Admin.route_selection, F.data == 'quit')
@log_dec(logger)
async def admin_quit(
        callback: types.CallbackQuery,
        state: context.FSMContext
):
    await state.clear()
    await delete_inline_keyboard(callback.message)
    await callback.answer()
    await callback.message.answer(ADMIN_EXIT_CONFIRMATION)


@router.callback_query(Admin.report_selection, F.data.startswith('report$'))
@log_dec(logger)
async def report_selection(
        callback: types.CallbackQuery,
        state: context.FSMContext
):
    report_id = int(callback.data.split("$")[1])

    if report_id in REPORT_TYPES:
        await state.update_data({'report_id': report_id})

        await delete_inline_keyboard(callback.message)
        await callback.message.answer(ENTER_PERIOD)
        await state.set_state(Admin.period_selection)


@router.message(Admin.period_selection, F.text)
@log_dec(logger)
async def period_selection(
        message: types.Message,
        state: context.FSMContext
):

    try:
        start, end = (value.strip() for value in message.text.split('-'))
    except ValueError:
        start, end = message.text.strip(), datetime.now().strftime('%d.%m.%Y')

    try:
        start, end = [
            datetime(*reversed(list(map(int, date.split('.')))))
            for date in (start, end)
        ]
    except (ValueError, TypeError):
        await message.answer(BAD_DATE_FORMAT)
        await message.answer(ENTER_PERIOD)
        return

    if start > end:
        await message.answer(BAD_PERIOD_RANGE)
        return

    await state.update_data({
        'start': start,
        'end': end
    })
    await message.answer(ENTER_EMAIL)
    await state.set_state(Admin.email_input)


@router.message(Admin.email_input, F.text)
@log_dec(logger)
async def email_input(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    if not check_is_email(message.text):
        await message.answer(BAD_EMAIL)
        return

    await state.update_data({'email': message.text})
    state_data = await state.get_data()  # noqa
    await message.answer(REPORT_PREPARING)

    # TODO: сформировать отчёт и вернуть URL гугл-таблицы
    report_url = 'Здесь будет ссылка на гугл-таблицу'

    await message.answer(REPORT_READY)
    await message.answer(report_url)
    await state.clear()
    await admin_welcome(message, state, session)
