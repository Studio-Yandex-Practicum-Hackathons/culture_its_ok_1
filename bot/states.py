from aiogram.fsm import state


class NewUser(state.StatesGroup):
    name_input = state.State()
    age_input = state.State()


class Route(state.StatesGroup):
    route_selection = state.State()
    reflection = state.State()
    point_search = state.State()


class Admin(state.StatesGroup):
    route_selection = state.State()
    email_input = state.State()
    report_selection = state.State()
