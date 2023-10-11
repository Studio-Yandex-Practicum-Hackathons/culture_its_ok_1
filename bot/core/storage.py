from aiogram.fsm.context import FSMContext
from aiogram.types import Message


class SimpleMemoryStateStorage:
    """Это хранилище используется только для обмена объектами типа Message и
    FSMContext между handlers.route.route_follow и handlers.route.route_quiz.
    """
    def __init__(self):
        self.message = None
        self.state = None

    def set_data(
            self,
            message: Message,
            state: FSMContext
    ):
        self.message = message
        self.state = state

    def get_data(self):
        return self.message, self.state


storage = SimpleMemoryStateStorage()
