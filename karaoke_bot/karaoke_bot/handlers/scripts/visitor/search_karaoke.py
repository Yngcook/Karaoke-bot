from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.visitor_states import KaraokeSearch
from karaoke_bot.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.handlers.scripts.common.register_telegram_user import register_telegram_user
from karaoke_bot.models.sqlalchemy_data_utils import subscribe_to_karaoke, get_karaoke_data_by_name
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, KaraokeNotFoundError, \
    EmptyFieldError, InvalidAccountStateError
from karaoke_bot.handlers.utils import format_subscribers_count
from .order_track import order_track_command
from karaoke_bot.states import owner_states, visitor_states
from karaoke_bot.localization.localization_manager import LocalizationManager
from karaoke_bot.localization.local_files.scripts.visitor.loc_search_karaoke import local_dict
from karaoke_bot.keyboards.keyboard_factory import KeyboardFactory


lm = LocalizationManager(local_dict=local_dict)
kf = KeyboardFactory(lm=lm)


async def search_karaoke_command(message: types.Message):
    await message.answer(
        text=lm.localize_text(
            search_karaoke_command.__name__,
            message.from_user.language_code,
            params=['messages', 'enter_name']
        ),
        parse_mode='HTML'
    )
    await KaraokeSearch.name.set()


async def callback_search_karaoke_command(callback: types.CallbackQuery):
    await callback.answer()
    callback.message.from_user = callback.from_user  # Чтобы вся информация была от пользователя, а не от бота
    await search_karaoke_command(callback.message)


async def search_karaoke(message: types.Message, state: FSMContext):
    fname = search_karaoke.__name__
    lg_code = message.from_user.language_code

    karaoke_name = message.text
    try:
        karaoke_data = get_karaoke_data_by_name(karaoke_name=karaoke_name, user_id=message.from_user.id)
    except KaraokeNotFoundError as e:
        print(f"ERROR OCCURRED: {e.args}")
        await message.reply(
            text=lm.localize_text(fname, lg_code, params=['messages', 'no_karaoke']),
            parse_mode='HTML'
        )
    else:
        subscribers_amount = karaoke_data['subscribers']['amount']
        caption = f"{lm.localize_text(fname, lg_code, params=['messages', 'karaoke'])} {karaoke_name}\n" \
                  f"{lm.localize_text(fname, lg_code, params=['messages', 'owner'])} @{karaoke_data['owner']['username']}\n" \
                  f"{lm.localize_text(fname, lg_code, params=['messages', 'subscribers'])}: {format_subscribers_count(subscribers_amount)}\n\n"

        if karaoke_data['description'] is not None:
            caption += karaoke_data['description']

        if karaoke_data['subscribers']['is_subscribed']:  # если пользователь уже подписан
            keyboard = kf.get_inline_keyboard(keyboard_name='keyboard_order_track', lg_code=lg_code)
            caption += lm.localize_text(fname, lg_code, params=['messages', 'already_sub'])
        else:
            keyboard = kf.get_inline_keyboard(
                keyboard_name='keyboard_subscribe',
                lg_code=lg_code,
                callbacks_data={1: f'subscribe_to {karaoke_name}'}
            )

        if karaoke_data['avatar_id'] is not None:
            await bot.send_photo(
                chat_id=message.from_user.id,
                photo=karaoke_data['avatar_id'],
                caption=caption,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await message.answer(caption, reply_markup=keyboard, parse_mode='HTML')


async def callback_subscribe_to_karaoke(callback: types.CallbackQuery, state: FSMContext):
    fname = callback_subscribe_to_karaoke.__name__
    lg_code = callback.from_user.language_code

    karaoke_name = callback.data.split(' ')[-1]
    user_id = callback.from_user.id

    await callback.message.edit_reply_markup()  # delete markup
    try:
        subscribe_to_karaoke(telegram_id=user_id, karaoke_name=karaoke_name)
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
        await register_telegram_user(callback.from_user)
        await callback_subscribe_to_karaoke(callback, state)
    except KaraokeNotFoundError as e:
        print(f"ERROR OCCURRED: {e.args}")
        await callback.message.answer(text=e.args[0])
    else:
        await callback.answer(
            text=lm.localize_text(fname, lg_code, params=['messages', 'you_sub']),
            show_alert=True
        )

        current_state = await state.get_state()
        match current_state:
            case owner_states.NewKaraoke.new_karaoke.state:
                await state.finish()
                await callback.message.edit_reply_markup(
                    reply_markup=kf.get_inline_keyboard(
                        keyboard_name='keyboard_already_sub',
                        lg_code=lg_code,
                        callbacks_data={2: f'get_qr_code {karaoke_name}'}
                    )
                )

            case _:
                await order_track_command(callback.message, state, callback.from_user.id)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(search_karaoke_command, commands=['search_karaoke'])
    dp.register_message_handler(search_karaoke_command, Text(startswith='search karaoke', ignore_case=True))

    dp.register_callback_query_handler(callback_search_karaoke_command, Text(equals='search_karaoke'), state='*')

    dp.register_message_handler(search_karaoke, state=KaraokeSearch.name)

    dp.register_callback_query_handler(callback_subscribe_to_karaoke, Text(startswith='subscribe_to'), state='*')
