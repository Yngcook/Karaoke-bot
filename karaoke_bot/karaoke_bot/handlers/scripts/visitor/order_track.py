from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.visitor_states import OrderTrack
from karaoke_bot.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.handlers.scripts.common.register_telegram_user import register_telegram_user
from karaoke_bot.karaoke_gram.karaoke import add_track_to_queue
from karaoke_bot.models.sqlalchemy_data_utils import get_selected_karaoke_data, add_performance_to_visitor
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, KaraokeNotFoundError, \
    EmptyFieldError, InvalidAccountStateError
from karaoke_bot.localization.localization_manager import LocalizationManager
from karaoke_bot.localization.local_files.scripts.visitor.loc_order_track import local_dict


lm = LocalizationManager(local_dict=local_dict)


async def callback_order_track_command(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    callback.message.from_user = callback.from_user  # Чтобы вся информация была от пользователя, а не от бота
    await order_track_command(message=callback.message, state=state, user_id=callback.from_user.id)


async def order_track_command(message: types.Message, state: FSMContext, user_id=None):
    fname = order_track_command.__name__
    lg_code = message.from_user.language_code

    if user_id is None:
        user_id = message.from_user.id

    try:
        karaoke_name, owner_id = get_selected_karaoke_data(telegram_id=user_id)
    except (EmptyFieldError, InvalidAccountStateError) as e:
        print(f"ERROR OCCURRED: {e}")

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(
            text=lm.localize_text(fname, lg_code, params=['buttons', 'yes']),
            callback_data='search_karaoke')
        )
        keyboard.insert(InlineKeyboardButton(
            text=lm.localize_text(fname, lg_code, params=['buttons', 'no']),
            callback_data='cancel')
        )

        await bot.send_message(
            chat_id=user_id,
            text=lm.localize_text(fname, lg_code, params=['messages', 'not_chosen_karaoke']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
        await register_telegram_user(message.from_user)
        await order_track_command(message, state, user_id)
    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
    else:
        await OrderTrack.link.set()
        async with state.proxy() as data:
            data['karaoke_name'] = karaoke_name
            data['owner_id'] = owner_id
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(
            text=lm.localize_text(fname, lg_code, params=['buttons', 'change_karaoke']),
            callback_data='change_selected_karaoke')
        )
        await bot.send_message(
            chat_id=user_id,
            text=lm.localize_text(fname, lg_code, params=['messages', 'send_track']) + karaoke_name,
            reply_markup=keyboard,
            parse_mode='HTML'
        )


async def add_link(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        karaoke_name = data.get('karaoke_name')
        owner_id = data.get('owner_id')

    try:
        add_performance_to_visitor(telegram_id=message.from_user.id, track_url=message.text)
    except (EmptyFieldError, InvalidAccountStateError) as e:
        print(f"ERROR OCCURRED: {e}")
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
    else:
        add_track_to_queue(user=message.from_user, karaoke_name=karaoke_name, owner_id=owner_id, track_url=message.text)
        await message.answer(
            text=lm.localize_text(
                add_link.__name__,
                message.from_user.language_code,
                params=['messages', 'track_added']
            )
        )
    finally:
        await state.finish()


async def link_is_invalid(message: types.Message, state: FSMContext):
    lg_code = message.from_user.language_code

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(
        text=lm.localize_text(order_track_command.__name__, lg_code, params=['buttons', 'change_karaoke']),
        callback_data='change_selected_karaoke')
    )

    async with state.proxy() as data:
        karaoke_name = data.get('karaoke_name')

    await message.reply(
        text=lm.localize_text(link_is_invalid.__name__, lg_code, params=['messages', 'link_invalid']) + karaoke_name,
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode='HTML'
    )


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(order_track_command, commands=['order_track'], state='*')
    dp.register_message_handler(
        order_track_command,
        Text(equals=["Order a track", "Заказать трек"], ignore_case=True),
        state='*'
    )
    dp.register_callback_query_handler(callback_order_track_command, Text(startswith='order_track'), state='*')

    dp.register_message_handler(
        add_link,
        Text(startswith=[
            'https://www.youtube.com/watch?v=',
            'https://youtu.be/',
            'https://xminus.me/track/'
        ]),
        state=OrderTrack.link
    )

    dp.register_message_handler(link_is_invalid, content_types='any', state=OrderTrack.link)
