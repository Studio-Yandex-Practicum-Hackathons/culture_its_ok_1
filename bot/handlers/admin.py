from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm import context
from core.logger import log_dec, logger_factory
from db.crud import user_crud, route_crud
from handlers.new_user import name_input
from handlers.route import route_selection
from sqlalchemy.ext.asyncio import AsyncSession
from core.utils import send_message_and_sleep
from core.states import Route, Admin
from services.google_report import GoogleReport

router = Router()
logger = logger_factory(__name__)

ADMIN_WELCOME = ('Добро пожаловать в административную зону. Пожалуйста, '
                 'выберите маршрут, по которому вы желаете получить отчёт')

ENTER_EMAIL = 'Введите email, которому будет предоставлен доступ к отчёту'


@router.message(Command('admin'), Route.selection)
@log_dec(logger)
async def cmd_admin(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    # TODO: проверить пароль, удалить инлайн-клавиатуры
    await message.answer(ADMIN_WELCOME)
    await state.set_state(Admin.route_selection)


@router.message(Admin.route_selection, F.text)
@log_dec(logger)
async def route_selection(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    routes = [
        route for route in
        await route_crud.get_all(session, sort='id asc')
    ]

    if message.text in routes:
        await state.set_data({'current_route': message.text})

        await message.answer(ENTER_EMAIL,
                             reply_markup=types.ReplyKeyboardRemove())
        await state.set_state(Admin.email_input)


@router.message(Admin.email_input, F.text)
@log_dec(logger)
async def email_input(
        message: types.Message,
        state: context.FSMContext,
        session: AsyncSession
):
    # TODO: провести валидацию введённого email
    await message.answer('Отчёт формируется, пожалуйста, подождите')
    state_data = await state.get_data()
    report = GoogleReport()

    header = [
        ['Отчёт по использованию бота'],
        ['Маршрут:', 'Маршрут 1'],
        ['Количество пользователей, воспользовавшихся ботом:', *[''] * 3, 50],
        ['из них'],
        ['прошли маршрут целиком', *[''] * 3, 40],
    ]

    object1 = [
        ['Объект 1'],
        ['Пользователь', 'Вопрос', 'Ответ'],
        ['Александр', 'Что думаете?', 'Выглядит не очень']
    ]

    object2 = [
        ['Объект 2'],
        ['Пользователь', 'Вопрос', 'Ответ'],
        ['Пётр', 'Как вы думаете, что это?', 'Титаник']
    ]

    report.set_title(f'Отчёт по маршруту {state_data["current_route"]}')
    report.set_header(header)
    report.add_rows(object1, object2)
    report.set_email(message.text)
    report_url = await report.create()

    msg = (f'Отчёт сформирован. Для доступа к нему перейдите по ссылке ниже, '
           f'под аккаунтом {message.text}')
    await send_message_and_sleep(message, msg)
    await message.answer(report_url)
    await state.clear()
