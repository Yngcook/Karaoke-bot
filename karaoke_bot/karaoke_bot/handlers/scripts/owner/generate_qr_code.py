from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.create_bot import bot
import os
import qrcode


async def callback_generate_qr_code(callback: types.CallbackQuery):
    await callback.answer()

    bot_user: types.User = await bot.get_me()
    delimeter = '-'
    karaoke_name = callback.data.split(' ')[1]
    url = f'https://t.me/{bot_user.username}?start=func=search_karaoke{delimeter}karaoke_name={karaoke_name}'

    qr_path = generate_qr_qcode(text=url, qr_id=callback.from_user.id)

    with open(qr_path, 'rb') as photo:
        await bot.send_photo(chat_id=callback.from_user.id, photo=photo)
    os.remove(qr_path)  # Удаляем сохраненное изображение после отправки


def generate_qr_qcode(text: str, qr_id: int, qr_foldername: str = 'qr_codes') -> str:
    qr = qrcode.make(text)

    qr_folderpath = os.path.join(os.getcwd(), qr_foldername)  # Создаем папку, если ее нет
    if not os.path.exists(qr_folderpath):
        os.makedirs(qr_folderpath)

    qr_path = os.path.join(qr_folderpath, f'qr_{qr_id}.png')
    qr.save(qr_path)
    return qr_path


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(callback_generate_qr_code, Text(startswith='get_qr_code'), state='*')
