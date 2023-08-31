from aiogram import Router, types
from core.logger import log_exceptions, logger_factory

router = Router()
logger = logger_factory(__name__)

MAX_ATTEMPTS = 3

INSTRUCTION = (
    'Мы заметили, что от вас получено несколько сообщений, которые мы не '
    'можем корректно обработать. Пожалуйста, прочитайте последние сообщения '
    'от бота и следуйте им. Вот несколько подсказок, которые могут помочь:\n'
    '- обратите внимание на верхнюю часть экрана. Если там указано "печатает" '
    'или "отправляет фото", значит бот готовит для вас информацию, просто '
    'немного подождите; \n'
    '- если на экране квиз (викторина), выберите один из вариантов, чтобы '
    'продолжить;\n'
    '- если бот задал вопрос. Пожалуйста, ответьте текстовым или голосовым '
    'сообщением;\n'
    '- возможно, бот ожидает от вас нажатия кнопки под каким-либо сообщением '
    'в чате.\n\n'
    'Если ничего из перечисленного вам не помогло, возможно, бот завис. В '
    'таком случае, приносим вам свои извинения. Вы можете перезапустить бота,'
    'нажав кнопку <u>Меню</u> => <u>Перезапустить</u> в левой нижней части '
    'экрана.'
)


class Counter:
    def __init__(self, threshold: int):
        self.threshold = threshold
        self.counter = 0

    def increase(self) -> None:
        self.counter += 1

    def reset(self) -> None:
        self.counter = 0

    def is_exceeded(self) -> bool:
        return self.counter > self.threshold


spam_counter = Counter(MAX_ATTEMPTS)


@router.message()
@log_exceptions(logger)
async def unexpected_message(message: types.Message):
    spam_counter.increase()

    if spam_counter.is_exceeded():
        await message.answer(INSTRUCTION)


@router.callback_query()
@log_exceptions(logger)
async def unexpected_callback(callback: types.CallbackQuery):
    spam_counter.increase()

    if spam_counter.is_exceeded():
        await callback.message.answer(INSTRUCTION)
