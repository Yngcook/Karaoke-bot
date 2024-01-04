from aiogram.dispatcher.filters.state import State, StatesGroup


class KaraokeSearch(StatesGroup):
    name = State()


class OrderTrack(StatesGroup):
    link = State()