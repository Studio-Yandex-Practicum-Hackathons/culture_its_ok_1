from aiogram.fsm import state


class NewUser(state.StatesGroup):
    name_input = state.State()
    age_input = state.State()


class Route(state.StatesGroup):
    selection = state.State()
    following = state.State()
    reflection = state.State()
    search = state.State()


class Admin(state.StatesGroup):
    route_selection = state.State()
    report_selection = state.State()
    period_selection = state.State()
    email_input = state.State()