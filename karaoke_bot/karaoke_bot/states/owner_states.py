from aiogram.dispatcher.filters.state import State, StatesGroup


class NewKaraoke(StatesGroup):
    name = State()
    # password = State()
    avatar = State()
    description = State()
    edit_name = State()
    edit_avatar = State()
    edit_description = State()
    confirm = State()
    new_karaoke = State()


class LapQueue(StatesGroup):
    pass


class QRCode(StatesGroup):
    text = State()