from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.models.sqlalchemy_data_utils import get_account_roles, get_visitor_karaokes_data,\
    get_owner_karaokes_data
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, EmptyFieldError
from karaoke_bot.handlers.scripts.common.register_telegram_user import register_telegram_user
import json
from karaoke_bot.create_bot import bot


async def menu_command(message: types.Message, state: FSMContext):
    await state.finish()

    try:
        is_visitor, is_owner, is_moderator, is_administrator = get_account_roles(message.from_user.id)
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
        await register_telegram_user(message.from_user)
        await menu_command(message=message, state=state)
    else:
        keyboard = InlineKeyboardMarkup()
        if is_visitor:
            keyboard.add(InlineKeyboardButton(text="My orders", callback_data='menu my_orders'))
        if is_owner:
            keyboard.insert(InlineKeyboardButton(text="My karaoke", callback_data='menu my_karaoke'))

        await message.answer('MENU', reply_markup=keyboard)


async def callback_menu_command(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    keyboard = InlineKeyboardMarkup()
    callback_data = callback.data.split(' ')[1:]
    match callback_data:
        case ('my_orders',):
            pass

        case ('my_karaoke',):
            keyboard.add(InlineKeyboardButton(text="Managed", callback_data='menu managed_karaoke'))
            keyboard.insert(InlineKeyboardButton(text="Membering", callback_data='menu membering_karaoke'))
            keyboard.add(InlineKeyboardButton(text='<< Back', callback_data='menu back'))
            await callback.message.edit_text('Information about your karaoke', reply_markup=keyboard)

        case ('managed_karaoke',):
            try:
                karaokes_data = get_owner_karaokes_data(telegram_id=callback.from_user.id)
            except EmptyFieldError as e:
                print(f"ERROR OCCURRED: {e}")
            else:
                async with state.proxy() as data:
                    data['karaokes_data'] = karaokes_data

                text = 'Information about your karaoke\n\n'
                for karaoke_name, karaoke_data in karaokes_data.items():
                    avatar_text = '✅ YES' if karaoke_data.get('avatar_id') else '❌ NO'
                    descr_text = '✅ YES' if karaoke_data.get('description') else '❌ NO'
                    is_active = '✅ ACTIVE' if karaoke_data['is_active'] else '❌ INACTIVE'

                    text += f"<b>KARAOKE</b>: {karaoke_name}\n" \
                            f"Avatar: {avatar_text}" \
                            f"Description: {descr_text}" \
                            f"Subscribers: {karaoke_data['subscribers_amount']}\n" \
                            f"Status: {is_active}\n\n"
                    keyboard.insert(InlineKeyboardButton(text=karaoke_name, callback_data=f'menu managed_karaoke {karaoke_name}'))
                keyboard.add(InlineKeyboardButton(text='<< Back to karaoke info', callback_data='menu my_karaoke'))
                await callback.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')

        case ('managed_karaoke', karaoke_name):
            async with state.proxy() as data:
                karaokes_data = data.get('karaokes_data')

            karaoke_data = karaokes_data.get(karaoke_name)
            if karaoke_data is not None:
                is_active = '✅ ACTIVE' if karaoke_data['is_active'] else '❌ INACTIVE'
                text = f"Status:{is_active}\nSubscribers: {karaoke_data['subscribers_amount']}\n"

                if karaoke_data.get('description'):
                    text += f"Description: {karaoke_data.get('description')}"

                keyboard.add(InlineKeyboardButton(text='<< Back to managed karaoke', callback_data='menu managed_karaoke'))
                avatar_id = karaoke_data.get('avatar_id')
                if avatar_id is not None:
                    await bot.send_photo(
                        chat_id=callback.from_user.id,
                        photo=avatar_id,
                        caption=text,
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )
                else:
                    await callback.message.answer(text=text, reply_markup=keyboard, parse_mode='HTML')

        case ('membering_karaoke',):
            try:
                karaokes_data = get_visitor_karaokes_data(telegram_id=callback.from_user.id)
            except EmptyFieldError as e:
                print(f"ERROR OCCURRED: {e}")
            else:
                text = 'KARAOKE  |  OWNER  |  SUBSCRIBERS  |  IS_ACTIVE\n\n'
                for karaoke_name, karaoke_data in karaokes_data.items():
                    username = karaoke_data['owner']['username']
                    is_active = '✅ ACTIVE' if karaoke_data['is_active'] else '❌ INACTIVE'
                    subscribers_amount = karaoke_data['subscribers_amount']
                    text += f"{karaoke_name}  |  @{username}  |  {subscribers_amount}  |  {is_active}\n"
                keyboard.add(InlineKeyboardButton(text='<< Back to karaoke info', callback_data='menu my_karaoke'))
                await callback.message.edit_text(text, reply_markup=keyboard)

        case ('back',):
            keyboard.add(InlineKeyboardButton(text="My karaoke", callback_data='menu my_karaoke'))
            keyboard.insert(InlineKeyboardButton(text="My orders", callback_data='menu my_orders'))
            await callback.message.edit_text('MENU', reply_markup=keyboard)


def register_handlers(dispatcher: Dispatcher):

    dispatcher.register_message_handler(menu_command, Text(equals=["menu", "меню"], ignore_case=True), state='*')
    dispatcher.register_message_handler(menu_command, commands=['menu'], state='*')

    dispatcher.register_callback_query_handler(callback_menu_command, Text(startswith='menu'))
