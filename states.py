from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    waiting_nsfw_toggle = State()
    waiting_antiraid_toggle = State()
