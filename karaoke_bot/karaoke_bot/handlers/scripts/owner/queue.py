from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.utils.markdown import hlink
from karaoke_bot.karaoke_gram.karaoke import ready_to_play_karaoke_list
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from karaoke_bot.karaoke_gram.karaoke import Karaoke
from karaoke_bot.karaoke_gram.types import TrackRemoved
from karaoke_bot.karaoke_gram.utils import find_first_match_karaoke, find_first_match_track
from karaoke_bot.states.owner_states import LapQueue


async def show_queue_command(message: types.Message):
    karaoke = find_first_match_karaoke(ready_to_play_karaoke_list, where={'owner_id': message.from_user.id})
    if karaoke is not None:
        index = 0
        track_number = 0
        while True:
            no_more_tracks = 0
            for user in karaoke.user_queue:
                try:
                    track = user.playlist[index]
                    track_number += 1
                    keyboard = InlineKeyboardMarkup()
                    keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
                    keyboard.insert(InlineKeyboardButton(
                        text="❌ Remove from queue",
                        callback_data=f'rm_from_queue {karaoke.name} {user.aiogram_user.id} {track.id}'))
                    await message.answer(f"{track_number}. {hlink('Track', track.url)}\n"
                                         f"Ordered by: @{user.aiogram_user.username}\n"
                                         f"Karaoke: {karaoke.name}",
                                         reply_markup=keyboard,
                                         parse_mode='HTML')
                except IndexError:
                    no_more_tracks += 1
            if no_more_tracks == len(karaoke.user_queue):
                break
            index += 1


async def get_lap_queue_command(message: types.Message, state: FSMContext):
    karaoke = find_first_match_karaoke(ready_to_play_karaoke_list, where={'owner_id': message.from_user.id})
    if karaoke is not None:
        async with state.proxy() as data:
            data['karaoke_name'] = karaoke.name

        await get_lap_queue_command_message(message, laps=karaoke.how_many_laps())
    else:
        await message.answer("You haven't created any karaoke yet")


async def get_lap_queue_command_message(message: types.Message, laps: int):
    if laps:
        keyboard = InlineKeyboardMarkup()
        for lap_index in range(laps):
            keyboard.insert(InlineKeyboardButton(text=f'{lap_index + 1}', callback_data=f'lap_queue lap {lap_index}'))
        await message.answer('Select a lap tracks', reply_markup=keyboard, parse_mode='HTML')
    else:
        await message.answer('There are no tracks ordered at the moment')


async def callback_get_lap_queue_command(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    async with state.proxy() as data:
        karaoke_name = data['karaoke_name']

    karaoke = find_first_match_karaoke(ready_to_play_karaoke_list, where={'name': karaoke_name})
    keyboard = InlineKeyboardMarkup()
    callback_data = callback.data.split(' ')[1:]
    match callback_data:
        case ['lap', lap_index]:
            lap_queue = karaoke.get_lap_queue(int(lap_index))
            text = f'<b>LAP {int(lap_index) + 1}</b>\n\n'
            for track_number, (user, track) in enumerate(lap_queue, start=1):
                name = user.aiogram_user.first_name
                username = user.aiogram_user.username
                if username is not None:
                    name = hlink(name, f'https://t.me/{username}')
                text += f"<b>TRACK {track_number}</b>\n" \
                        f"Visitor name: {name}\n" \
                        f"Link: {hlink('link_to_track', track.url)}\n\n"

                keyboard.insert(InlineKeyboardButton(
                    f"{track_number}",
                    callback_data=f'lap_queue track {lap_index} {track_number} {track.id}')
                )

            keyboard.add(InlineKeyboardButton('<< Back', callback_data='lap_queue back_to laps'))
            await callback.message.edit_text(
                text,
                reply_markup=keyboard,
                disable_web_page_preview=True,
                parse_mode='HTML'
            )

        case ['back_to', 'laps']:
            await callback.message.delete()
            await get_lap_queue_command_message(message=callback.message, laps=karaoke.how_many_laps())

        case ['track', lap_index, track_number, track_id]:
            user_by_track = karaoke.find_first_user_by_track(where={'id': int(track_id)})
            if user_by_track is not None:
                user, track = user_by_track

                name = user.aiogram_user.first_name
                text = f"<b>LAP {int(lap_index) + 1}   TRACK {track_number}</b>\n" \
                       f"Visitor name: {name}\n" \
                       f"Link: {hlink('link_to_track', track.url)}"

                keyboard.add(InlineKeyboardButton(text="✅ Set to perform", callback_data='set_to_perform'))
                keyboard.insert(InlineKeyboardButton(
                    text="❌ Remove from queue",
                    callback_data=f'rm_from_queue {karaoke.name} {user.aiogram_user.id} {lap_index} {track.id}')
                )
                keyboard.add(InlineKeyboardButton('<< Back to lap', callback_data=f'lap_queue lap {lap_index}'))
                await callback.message.edit_text(text, reply_markup=keyboard, parse_mode='HTML')


async def callback_remove_from_queue(callback: types.CallbackQuery):
    await callback.answer()
    karaoke_name, user_id, lap_number, track_id = callback.data.replace('rm_from_queue ', '').split(' ')

    karaoke = find_first_match_karaoke(ready_to_play_karaoke_list, where={'owner_id': callback.from_user.id})
    if karaoke is not None:
        user = karaoke.find_first_match_user(where={'id': int(user_id)})
        if user is not None:
            user.remove_track(track_id=int(track_id))

            text = callback.message.html_text + f"\nTrack status: ❌ Removed"
            await callback.message.edit_text(text, parse_mode='HTML')
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(
                text="Restore 🔧",
                callback_data=f'restore track {karaoke_name} {user_id} {track_id}')
            )
            keyboard.add(InlineKeyboardButton('<< Back to lap', callback_data=f'lap_queue lap {lap_number}'))
            await callback.message.edit_reply_markup(keyboard)


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(show_queue_command, commands=['show_queue'])
    dp.register_message_handler(get_lap_queue_command, commands=['get_lap_queue'])
    dp.register_callback_query_handler(callback_remove_from_queue, Text(startswith='rm_from_queue'))

    dp.register_callback_query_handler(callback_get_lap_queue_command, Text(startswith='lap_queue'))
