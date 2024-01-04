from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.states.visitor_states import OrderTrack
from karaoke_bot.create_bot import bot
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from karaoke_bot.models.sqlalchemy_data_utils import get_visitor_karaoke_names, change_selected_karaoke,\
    get_karaoke_owner_id
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError, KaraokeNotFoundError, \
    EmptyFieldError, InvalidAccountStateError


async def callback_change_selected_karaoke(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.edit_reply_markup()  # delete markup

    keyboard = InlineKeyboardMarkup()
    match callback.data.split(' '):
        case ['change_selected_karaoke']:
            try:
                karaoke_names = get_visitor_karaoke_names(telegram_id=callback.from_user.id)
            except EmptyFieldError as e:
                print(f"ERROR OCCURRED: {e}")
            else:
                async with state.proxy() as data:
                    karaoke_name = data.get('karaoke_name')
                # TODO обдумать случай сообщения если будет всего одно караоке т.е пустой text_list
                # TODO продумать как будет выглядит меню кнопок если караоке будет очень много
                text_list = ''
                for index, kname in enumerate(karaoke_names - {karaoke_name}):  # убираем из множества текущее караоке
                    text_list += f'\n– {kname}'
                    button = InlineKeyboardButton(text=kname, callback_data=f'change_selected_karaoke {kname}')

                    if index % 2 == 0:
                        keyboard.add(button)
                    else:
                        keyboard.insert(button)

                keyboard.add(InlineKeyboardButton(text="🔍 Search karaoke", callback_data='search_karaoke'))

                await callback.message.answer(
                    f"Select <b>karaoke</b> where you want to order a track.\n\nYour karaoke list:{text_list}",
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
        case ['change_selected_karaoke', karaoke_name]:
            try:
                change_selected_karaoke(telegram_id=callback.from_user.id, karaoke_name=karaoke_name)
            except KaraokeNotFoundError as e:
                print(f"ERROR OCCURRED: {e}")
            else:  # если удалось поменять selected_karaoke, пробуем узнать owner_id
                try:
                    owner_id = get_karaoke_owner_id(karaoke_name=karaoke_name)
                except EmptyFieldError as e:
                    print(f"ERROR OCCURRED: {e}")
                else:
                    async with state.proxy() as data:
                        data['karaoke_name'] = karaoke_name
                        data['owner_id'] = owner_id

                    keyboard.add(InlineKeyboardButton(text="Change karaoke", callback_data='change_selected_karaoke'))
                    await bot.send_message(
                        chat_id=callback.from_user.id,
                        text=f"Please send a link to the track on YouTube or XMinus\n\n"
                             f"<b>Selected karaoke:</b> {karaoke_name}",
                        reply_markup=keyboard,
                        parse_mode='HTML'
                    )


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(
        callback_change_selected_karaoke,
        Text(startswith='change_selected_karaoke'),
        state=OrderTrack.link
    )
