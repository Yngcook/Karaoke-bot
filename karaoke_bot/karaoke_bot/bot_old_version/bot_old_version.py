from aiogram.utils import executor
from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher, FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,\
    InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters import Text
import random
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.utils.markdown import hlink
from unique_links_parse import get_unique_links, load_links_by_user_id
from sqlalchemy_orm import VisitorPerformance, Recommendations, Base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import time
import csv
import os


print(f"Текущий рабочий каталог: {os.getcwd()}")


class FSMOrderTrack(StatesGroup):
    track_url = State()


class FSMMassMessage(StatesGroup):
    text = State()
    image = State()
    confirm = State()


async def start(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    if message.from_user.id != admin_id:
        keyboard.add(KeyboardButton("Order a track"))
        keyboard.add(KeyboardButton("Join a group of karaoke lovers"))
    else:
        keyboard.add(KeyboardButton("Get next link round"))

    bot_info = await bot.get_me()
    await message.answer(f"Welcome, {message.from_user.first_name}!\nI'm  - <b>{bot_info.first_name}</b>, "
                         f"the telegram bot of my favorite Venue bar. "
                         f"And I'm here to help you sing as many songs as possible! "
                         f"I hope you warmed up your vocal cords. 😏",
                         parse_mode='html',
                         reply_markup=keyboard)


async def get_next_link_round_command(message: types.Message):
    counter_empty = 0
    for user_id, value in user_ids.items():
        list_links, username = value
        if len(list_links):
            await message.answer(f"{hlink('Track', list_links.pop(0))} ordered by @{username}", parse_mode='HTML')
        else:
            counter_empty += 1

    if counter_empty == len(user_ids):
        await message.answer('Oops, Seems the songs are over.')


async def order_track_command(message: types.Message):
    await message.answer('Good! Add youtube link 😉')
    await FSMOrderTrack.track_url.set()


async def state_order_track_is_invalid(message: types.Message):
    await message.answer('You added the link incorrectly, please try again 😉')


async def add_link(message: types.Message, state: FSMContext):
    await state.finish()

    user_id = message.from_user.id

    if user_id not in user_ids:
        user_ids[user_id] = ([], message.from_user.username)

    user_ids[user_id][0].append(message.text)
    print(message.text)
    performance = VisitorPerformance(user_id=user_id, url=message.text, created_at=message.date)
    session.add(performance)
    session.commit()

    await message.answer('Success! Sing better than the original, I believe in you 😇')
    await get_recommendation(message)


async def get_recommendation(message: types.Message):
    user_id = message.from_user.id

    links = links_by_user_id.get(str(user_id))
    if links:
        link = links.pop(random.randint(0, len(links) - 1))
        type_link = 'user_link'
    else:
        link = random.choice(unique_links)
        type_link = 'random_link'

    rec_message = await message.answer(f"{link}\n\nTest recommendation", parse_mode='HTML')

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Order this track", callback_data=f'order_this_track'))
    await rec_message.edit_reply_markup(keyboard)

    recommendation = Recommendations(user_id=user_id, message_id=rec_message.message_id, url=link, rec_type=type_link,
                                     is_accepted=False, created_at=message.date, updated_at=message.date)
    session.add(recommendation)
    session.commit()


async def callback_order_this_track(callback: types.CallbackQuery):
    recommendation = session.query(Recommendations).filter(Recommendations.message_id == callback.message.message_id).first()
    # Проверить когда может придти None?
    recommendation.is_accepted = True
    recommendation.updated_at = callback.message.date

    text = callback.message.text.replace('\n\nTest recommendation', '')
    performance = VisitorPerformance(user_id=callback.from_user.id,
                                     url=text,
                                     created_at=callback.message.date)
    session.add(performance)

    if callback.from_user.id not in user_ids:
        user_ids[callback.from_user.id] = ([], callback.from_user.username)

    user_ids[callback.from_user.id][0].append(recommendation.url)

    await callback.answer('Success! Sing better than the original, I believe in you 😇')
    await callback.message.edit_text(f"✅ {hlink('Track', recommendation.url)} is ordered", parse_mode='HTML')
    session.commit()


async def join_a_group(message: types.Message):
    await message.answer('https://t.me/+JPb01AZkQgxkOGMy')


async def send_hello_text(message: types.Message):
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)

    if message.from_user.id != admin_id:
        keyboard.add(KeyboardButton("Order a track"))
        keyboard.add(KeyboardButton("Join a group of karaoke lovers"))
    else:
        keyboard.add(KeyboardButton("Get next link round"))
    await message.answer('Hello', reply_markup=keyboard)


async def mass_message(message: types.Message):
    await message.answer("<b>Mass Message Constructor</b>", parse_mode='HTML')

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Skip', callback_data='mass_message_skip text'))
    await message.answer("Please enter the 💬 <b>TEXT</b> (if any) for the message",
                         reply_markup=keyboard,
                         parse_mode='HTML')
    await FSMMassMessage.text.set()


async def mass_message_text_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['mass_message_text'] = message.html_text

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Skip', callback_data='mass_message_skip image'))
    await message.answer("Great!")
    await message.answer("Now please upload the 🖼 <b>IMAGE</b> (if any) for the message",
                         reply_markup=keyboard,
                         parse_mode='HTML')
    await FSMMassMessage.image.set()


async def mass_message_image_registration(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['mass_message_image_id'] = message.photo[0].file_id
    await mass_message_confirm(message.from_user.id, state)


async def state_mass_message_image_is_invalid(message: types.Message):
    await message.reply("It seems you sent something wrong\nPlease send a <b>IMAGE</b> to the mass message\n\n",
                        parse_mode='HTML')


async def mass_message_confirm(user_id, state: FSMContext):

    confirm_text = "<b>CONFIRM SENDING</b>"
    async with state.proxy() as data:
        text = data.get('mass_message_text')
        text = confirm_text if text is None else f'{confirm_text}\n\nMESSAGE TEXT:\n{text}'
        image_id = data.get('mass_message_image_id')

    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton('✅ Confirm and Send', callback_data='mass_message send'))
    keyboard.insert(InlineKeyboardButton('✏️ Edit', callback_data='mass_message edit'))
    keyboard.add(InlineKeyboardButton('❌ Delete', callback_data='mass_message delete'))

    if image_id is not None:
        await bot.send_photo(chat_id=user_id, photo=image_id, caption=text, reply_markup=keyboard, parse_mode='HTML')
    else:
        await bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard, parse_mode='HTML')

    await FSMMassMessage.confirm.set()


async def callback_mass_message_confirm(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split(' ')[-1]
    await callback.answer()

    keyboard = InlineKeyboardMarkup()
    if action == 'send':
        keyboard.add(InlineKeyboardButton('✅ Send', callback_data='mass_message force_send'),
                     InlineKeyboardButton('<< Back', callback_data='mass_message back'))
        await callback.message.edit_reply_markup(keyboard)

    elif action == 'force_send':
        await callback.answer('✅ Mass message sent successfully!', show_alert=True)
        await callback.message.delete()

        async with state.proxy() as data:
            text = data.get('mass_message_text')
            image_id = data.get('mass_message_image_id')

        await state.finish()
        await send_mass_message(sender_id=callback.from_user.id, text=text, image_id=image_id)

    elif action == 'edit':
        keyboard.add(InlineKeyboardButton('💬 Edit text', callback_data='mass_message edit_text'))
        keyboard.insert(InlineKeyboardButton('🖼 Edit image', callback_data='mass_message edit_image'))
        keyboard.add(InlineKeyboardButton('<< Back', callback_data='mass_message back'))
        await callback.message.edit_reply_markup(keyboard)

    elif action == 'delete':
        keyboard.add(InlineKeyboardButton('❌ Delete', callback_data='mass_message force_delete'),
                     InlineKeyboardButton('<< Back', callback_data='mass_message back'))
        await callback.message.edit_reply_markup(keyboard)

    elif action == 'force_delete':
        await callback.message.answer('❌ Mass message deleted')
        await callback.message.delete()
        await state.finish()

    elif action == 'back':
        keyboard.add(InlineKeyboardButton('✅ Confirm and Send', callback_data='mass_message send'))
        keyboard.insert(InlineKeyboardButton('✏️ Edit', callback_data='mass_message edit'))
        keyboard.add(InlineKeyboardButton('❌ Delete', callback_data='mass_message delete'))
        await callback.message.edit_reply_markup(keyboard)


async def callback_mass_message_skip(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()

    skiptype = callback.data.split(' ')[-1]
    if skiptype == 'text':
        await callback.message.answer("Please upload the 🖼 <b>IMAGE</b> for the message", parse_mode='HTML')
        await FSMMassMessage.image.set()
    if skiptype == 'image':
        await FSMMassMessage.confirm.set()
        await mass_message_confirm(callback.from_user.id, state)


async def send_mass_message(sender_id: int, text: str, image_id: str):

    with open('id_url_all.csv', encoding='u8') as fi:
        unique_user_ids = set(int(row['user_id']) for row in csv.DictReader(fi))

    user_ids = session.query(VisitorPerformance.user_id.distinct()).all()

    for user_id, in user_ids:  # type(user_id) - <tuple[int]>
        unique_user_ids.add(user_id)

    count_sended = 0
    for user_id in unique_user_ids:
        try:
            if text is not None:
                if image_id is not None:
                    await bot.send_photo(chat_id=user_id, photo=image_id, caption=text, parse_mode='HTML')
                else:
                    await bot.send_message(chat_id=user_id, text=text, parse_mode='HTML')
            else:
                await bot.send_photo(chat_id=user_id, photo=image_id, parse_mode='HTML')
            print(f'Сообщение доставлено {user_id}')
            count_sended += 1
            time.sleep(0.1)  # Можно отправлять 30 сообщений в секунду

        except Exception as e:
            print(f'Возникла ошибка при отправлении - {user_id}: {str(e)}')

    await bot.send_message(chat_id=sender_id,
                           text=f'The message was sent to {count_sended}/{len(unique_user_ids)} users')


async def cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Ok")
        return None
    await state.finish()
    await message.reply("Ok")


def register_handlers(dispatcher: Dispatcher):

    dispatcher.register_message_handler(cancel_command, Text(equals='cancel', ignore_case=True), state='*')
    dispatcher.register_message_handler(cancel_command, commands=['cancel'], state='*')

    dispatcher.register_message_handler(start, commands=['start'], state='*')
    dispatcher.register_message_handler(join_a_group, Text(equals='Join a group of karaoke lovers', ignore_case=True))

    dispatcher.register_message_handler(order_track_command, commands=['order_track'])
    dispatcher.register_message_handler(order_track_command, Text('Order a track', ignore_case=True))

    dispatcher.register_message_handler(get_next_link_round_command, lambda message: message.from_user.id == admin_id,
                                        commands=['get_next_link_round'])
    dispatcher.register_message_handler(get_next_link_round_command, lambda message: message.from_user.id == admin_id,
                                        Text('Get next link round'))

    dispatcher.register_message_handler(add_link,
                                        Text(startswith=['https://www.youtube.com/watch?v=',
                                                         'https://youtu.be/',
                                                         'https://xminus.me/track/',
                                                         'https://x-minus.cc/track/',
                                                         'https://x-minus.me/track/',
                                                         'https://x-minus.pro/track/',
                                                         'https://x-minus.club/track/',
                                                         'https://xm-rus.top/track/']),
                                        state=FSMOrderTrack.track_url)
    dispatcher.register_message_handler(state_order_track_is_invalid, content_types='any',
                                        state=FSMOrderTrack.track_url)

    dispatcher.register_callback_query_handler(callback_order_this_track, Text(startswith='order_this_track'))

    dispatcher.register_message_handler(mass_message,
                                        lambda message: message.from_user.id in [345705084, 375571119, 134566371],
                                        commands=['mass_message'])

    dispatcher.register_message_handler(mass_message_text_registration, state=FSMMassMessage.text)

    dispatcher.register_message_handler(mass_message_image_registration,
                                        content_types=['photo'],
                                        state=FSMMassMessage.image)
    dispatcher.register_message_handler(state_mass_message_image_is_invalid,
                                        content_types='any',
                                        state=FSMMassMessage.image)

    dispatcher.register_callback_query_handler(callback_mass_message_confirm,
                                               Text(equals=['mass_message send',
                                                            'mass_message force_send',
                                                            'mass_message edit',
                                                            'mass_message delete',
                                                            'mass_message force_delete',
                                                            'mass_message back']),
                                               state=FSMMassMessage.confirm)

    dispatcher.register_callback_query_handler(callback_mass_message_skip,
                                               Text(equals=['mass_message_skip text', 'mass_message_skip image']),
                                               state=[FSMMassMessage.text, FSMMassMessage.image])

    dispatcher.register_message_handler(send_hello_text, content_types='any')


if __name__ == "__main__":
    # подключение к бд
    debug_mode = False
    if debug_mode:
        engine = create_engine('sqlite:///karaoke_old_version_debug.db')
    else:
        engine = create_engine('sqlite:///karaoke_old_version.db')
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    API_TOKEN = "5761106314:AAHRTn5aJwpIiswWNoRpphpuZh38GD-gsP0"
    # API_TOKEN = "6157408135:AAGNyYeInRXTrbGVdx_qXaiWHgDxTJP2b5w"  # мой тестовый бот
    bot = Bot(token=API_TOKEN)

    storage = MemoryStorage()
    dispatcher = Dispatcher(bot, storage=storage)

    user_ids = {}

    admin_id = 1206756552  # владелец бара
    # admin_id = 345705084  # kuks_51
    # admin_id = 375571119  # gra4evp
    # admin_id = 134566371  # gleb_kukuruz
    # admin_id = 5774261029  # Rayan - ведущий

    unique_links = get_unique_links('id_url_all.csv')
    links_by_user_id = load_links_by_user_id('links_by_user_id.json')

    register_handlers(dispatcher)
    executor.start_polling(dispatcher, skip_updates=True)
