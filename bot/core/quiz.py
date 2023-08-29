from typing import Any
from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext


class QuizState:
    def __init__(self):
        self.state = False

    def set_state(self, state: bool):
        self.state = state

    def get_state(self):
        return self.state


class FSMContextStorage:
    def __init__(self):
        self.context = None

    def set_context(self, context: FSMContext):
        self.context = context

    def get_context(self):
        return self.context


quiz_state = QuizState()
fsm_context = FSMContextStorage()


class QuizFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return quiz_state.get_state()
