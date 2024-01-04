from aiogram import types, Dispatcher
from karaoke_bot.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.models.sqlalchemy_data_utils import get_selected_karaoke_data
from karaoke_bot.models.sqlalchemy_exceptions import EmptyFieldError, InvalidAccountStateError
from karaoke_bot.karaoke_gram.karaoke import find_first_match_karaoke
from aiogram.utils.markdown import hlink


async def show_my_orders_command(message: types.Message):
    try:
        karaoke_name, owner_id = get_selected_karaoke_data(message.from_user.id)
    except (EmptyFieldError, InvalidAccountStateError) as e:
        print(f"ERROR OCCURRED: {e}")

        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(text="✅ Yes", callback_data='search_karaoke'))
        keyboard.insert(InlineKeyboardButton(text="❌ No", callback_data='cancel'))
        await bot.send_message(
            chat_id=message.from_user.id,
            text="You have not chosen any karaoke where you can order music.\n\nGo to karaoke search?",
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
    else:
        karaoke = find_first_match_karaoke(karaoke_name)
        if karaoke is None:
            await message.answer("🗒 You haven't ordered any tracks yet")
        else:
            user = karaoke.find_first_match_user(where={'id': message.from_user.id})
            queue_length = len(user.playlist)
            if queue_length:
                for i in range(queue_length):
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
                    keyboard.insert(InlineKeyboardButton(text="❌ Remove", callback_data=f'rm_track'))
                    await message.answer(f"{i + 1}. {hlink('Track', user.playlist[i].url)}\n"
                                         f"Karaoke: {karaoke.name}",
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
            else:
                await message.answer("🗒 You haven't ordered any tracks yet")


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_my_orders_command, commands=['show_my_orders'])
