# модуль нужен для избежания циклического импорта между visitor.search_karaoke и common.other
from aiogram import types, Dispatcher
from karaoke_bot.models.sqlalchemy_data_utils import create_or_update_telegram_profile


async def register_telegram_user(user: types.User):
    try:
        create_or_update_telegram_profile(user)
    except Exception as e:
        print(f"Error occurred: {e}")