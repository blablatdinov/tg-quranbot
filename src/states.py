from aiogram.dispatcher.filters.state import State, StatesGroup


class AyatSearchSteps(StatesGroup):
    """Состояния для поиска аятов."""

    insert_into_search_mode = State()
