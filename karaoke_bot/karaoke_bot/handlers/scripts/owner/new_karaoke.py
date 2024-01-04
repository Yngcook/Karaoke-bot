from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from string import ascii_letters, digits

from karaoke_bot.create_bot import bot
from karaoke_bot.states.owner_states import NewKaraoke
from karaoke_bot.handlers.scripts.common.register_telegram_user import register_telegram_user
from karaoke_bot.handlers.scripts.visitor.search_karaoke import search_karaoke
from karaoke_bot.models.sqlalchemy_data_utils import karaoke_not_exists, create_karaoke, create_karaoke_session
from karaoke_bot.models.sqlalchemy_exceptions import TelegramProfileNotFoundError
from karaoke_bot.localization.localization_manager import LocalizationManager
from karaoke_bot.localization.local_files.scripts.owner.loc_new_karaoke import local_dict
from karaoke_bot.keyboards.keyboard_factory import KeyboardFactory


lm = LocalizationManager(local_dict=local_dict)
kf = KeyboardFactory(lm=lm)


async def new_karaoke_command(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['owner'] = message.from_user

    await message.answer(
        text=lm.localize_text(
            new_karaoke_command.__name__,
            message.from_user.language_code,
            params=['messages', 'new_name']
        ),
        parse_mode='HTML'
    )

    await NewKaraoke.name.set()


async def karaoke_name_registration(message: types.Message, state: FSMContext):
    fname = karaoke_name_registration.__name__
    lg_code = message.from_user.language_code

    karaoke_name = message.text
    if karaoke_not_exists(karaoke_name):
        async with state.proxy() as data:
            data['karaoke_name'] = karaoke_name
            data['message_karaoke_name'] = message

        current_state = await state.get_state()
        if current_state == 'NewKaraoke:name':
            await NewKaraoke.avatar.set()
            keyboard = InlineKeyboardMarkup()
            keyboard.add(InlineKeyboardButton(
                text=lm.localize_text(fname, lg_code, params=['buttons', 'skip']),
                callback_data='new_karaoke skip avatar')
            )
            await message.answer(
                text=lm.localize_text(fname, lg_code, params=['messages', 'now_send_photo']),
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        else:
            await message.answer(
                text=lm.localize_text(fname, lg_code, params=['messages', 'success_update']),
                reply_markup=kf.get_inline_keyboard('keyboard_back_to', lg_code),
                parse_mode='HTML'
            )
    else:
        await message.reply(
            text=lm.localize_text(fname, lg_code, params=['messages', 'already_taken']),
            parse_mode='HTML'
        )


async def karaoke_name_is_invalid(message: types.Message):
    await message.reply(
        text=lm.localize_text(
            karaoke_name_is_invalid.__name__,
            message.from_user.language_code,
            params=['messages', 'invalid_name']
        ),
        parse_mode='HTML'
    )


async def karaoke_avatar_registration(message: types.Message, state: FSMContext):
    fname = karaoke_avatar_registration.__name__
    lg_code = message.from_user.language_code

    async with state.proxy() as data:
        data['karaoke_avatar'] = message.photo[0].file_id

    current_state = await state.get_state()
    if current_state == 'NewKaraoke:avatar':
        await NewKaraoke.description.set()
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton(
            text=lm.localize_text(fname, lg_code, params=['buttons', 'skip']),
            callback_data='new_karaoke skip description')
        )
        await message.answer(
            text=lm.localize_text(fname, lg_code, params=['messages', 'send_description']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        await message.answer(
            text=lm.localize_text(fname, lg_code, params=['messages', 'avatar_updated']),
            reply_markup=kf.get_inline_keyboard('keyboard_back_to', lg_code),
            parse_mode='HTML'
        )


async def karaoke_avatar_is_invalid(message: types.Message):
    await message.reply(
        text=lm.localize_text(
            karaoke_avatar_is_invalid.__name__,
            message.from_user.language_code,
            params=['messages', 'invalid_avatar']
        ),
        parse_mode='HTML'
    )


async def karaoke_description_registration(message: types.Message, state: FSMContext):
    lg_code = message.from_user.language_code

    async with state.proxy() as data:
        data['description'] = message.html_text
    current_state = await state.get_state()
    if current_state == 'NewKaraoke:description':
        await new_karaoke_command_confirm(message, state)
    else:
        await message.answer(
            text=lm.localize_text(
                karaoke_description_registration.__name__,
                lg_code,
                params=['messages', 'description_updated']
            ),
            reply_markup=kf.get_inline_keyboard('keyboard_back_to', lg_code),
            parse_mode='HTML'
        )


async def karaoke_description_is_invalid(message: types.Message) -> None:
    await message.reply(
        text=lm.localize_text(
            karaoke_description_is_invalid.__name__,
            message.from_user.language_code,
            params=['messages', 'description_invalid']
        ),
        parse_mode='HTML'
    )


async def new_karaoke_command_confirm(
        message: types.Message,
        state: FSMContext,
        keyboard: InlineKeyboardMarkup | None = None
) -> None:

    fname = new_karaoke_command_confirm.__name__
    lg_code = message.from_user.language_code

    confirm_text = lm.localize_text(fname, lg_code, params=['messages', 'confirm'])
    async with state.proxy() as data:
        name = data.get('karaoke_name')
        avatar_id = data.get('karaoke_avatar')
        description = data.get('description')

    local_name = lm.localize_text(fname, lg_code, params=['messages', 'name'])
    text = confirm_text + local_name + name
    if description is not None:
        text += lm.localize_text(fname, lg_code, params=['messages', 'description']) + description

    if keyboard is None:
        keyboard = kf.get_inline_keyboard('keyboard_confirm', lg_code)

    if avatar_id is not None:
        await message.answer_photo(photo=avatar_id, caption=text, reply_markup=keyboard, parse_mode='HTML')
    else:
        await message.answer(text, reply_markup=keyboard, parse_mode='HTML')


async def callback_new_karaoke(callback: types.CallbackQuery, state: FSMContext):
    fname = callback_new_karaoke.__name__
    lg_code = callback.from_user.language_code

    # Нужно заменить lg_code на код пользователя при вызове функции из callback_new_karaoke и передаче message
    # Потому что будет передаваться message самого бота
    callback.message.from_user.language_code = lg_code

    user_id = callback.from_user.id

    await callback.answer()

    keyboard = InlineKeyboardMarkup()
    callback_data = callback.data.split(' ')[1:]
    match callback_data:
        case ('create',):
            await callback.message.edit_reply_markup(kf.get_inline_keyboard('keyboard_create', lg_code))

        case ('create', 'force'):
            await callback.message.delete()

            async with state.proxy() as data:
                message_karaoke_name: types.message = data.get('message_karaoke_name')
            await state.set_state(NewKaraoke.new_karaoke)
            await register_karaoke(state, lg_code=callback.from_user.language_code)
            await search_karaoke(message=message_karaoke_name, state=state)

        case ('edit',):
            await callback.message.edit_reply_markup(kf.get_inline_keyboard('keyboard_edit', lg_code))

        case ('edit', 'name'):
            await NewKaraoke.edit_name.set()
            await callback.message.answer(
                text=lm.localize_text(fname, lg_code, params=['messages', 'edit_name']),
                parse_mode='HTML'
            )

        case ('edit', 'avatar'):
            await NewKaraoke.edit_avatar.set()
            await callback.message.answer(
                text=lm.localize_text(fname, lg_code, params=['messages', 'edit_avatar']),
                parse_mode='HTML'
            )

        case ('edit', 'description'):
            await NewKaraoke.edit_description.set()
            await callback.message.answer(
                text=lm.localize_text(fname, lg_code, params=['messages', 'edit_description']),
                parse_mode='HTML'
            )

        case ('skip', 'avatar'):
            await NewKaraoke.description.set()
            await callback.message.edit_reply_markup()  # delete markup
            keyboard.add(InlineKeyboardButton(
                text=lm.localize_text(fname, lg_code, params=['buttons', 'skip']),
                callback_data='new_karaoke skip description')
            )
            await callback.message.answer(
                text=lm.localize_text(fname, lg_code, params=['messages', 'skip_avatar']),
                reply_markup=keyboard,
                parse_mode='HTML'
            )

        case ('skip', 'description'):
            await callback.message.edit_reply_markup()  # delete markup
            await new_karaoke_command_confirm(message=callback.message, state=state)

        case ('cancel',):
            await callback.message.edit_reply_markup(kf.get_inline_keyboard('keyboard_cancel', lg_code))

        case ('cancel', 'force'):
            await callback.message.answer(
                text=lm.localize_text(fname, lg_code, params=['messages', 'cancel_force'])
            )
            await callback.message.delete()
            await state.finish()

        case ('back',):
            await callback.message.edit_reply_markup(kf.get_inline_keyboard('keyboard_confirm', lg_code))

        case ('back', 'confirmation'):
            await callback.message.delete()
            await new_karaoke_command_confirm(message=callback.message, state=state)

        case ('back', 'editing'):
            await callback.message.delete()
            await new_karaoke_command_confirm(
                message=callback.message,
                state=state,
                keyboard=kf.get_inline_keyboard('keyboard_edit', lg_code)
            )


async def register_karaoke(state: FSMContext, lg_code: str):
    fname = register_karaoke.__name__

    async with state.proxy() as data:
        owner: types.User = data.get('owner')
        karaoke_name: str = data.get('karaoke_name')
        avatar_id: str = data.get('karaoke_avatar')
        description: str = data.get('description')

    try:
        create_karaoke(telegram_id=owner.id, name=karaoke_name, avatar_id=avatar_id, description=description)
        create_karaoke_session(karaoke_name=karaoke_name)
    except TelegramProfileNotFoundError as e:
        print(f"ERROR OCCURRED: {e}")
        await register_telegram_user(owner)
        await register_karaoke(state, lg_code)
    except Exception as e:
        print(f"ERROR OCCURRED: {e}")
        await bot.send_message(
            chat_id=owner.id,
            text=lm.localize_text(fname, lg_code, params=['messages', 'fail'])
        )
    else:
        await bot.send_message(
            chat_id=owner.id,
            text=lm.localize_text(fname, lg_code, params=['messages', 'success']),
            parse_mode='HTML'
        )


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(new_karaoke_command, commands=['new_karaoke'])

    dp.register_message_handler(
        karaoke_name_registration,
        lambda message: all(c in ascii_letters + digits + '$*&_@' for c in message.text) and len(message.text) <= 20,
        state=[NewKaraoke.name, NewKaraoke.edit_name]
    )

    dp.register_message_handler(
        karaoke_name_is_invalid,
        content_types='any',
        state=[NewKaraoke.name, NewKaraoke.edit_name]
    )

    dp.register_message_handler(
        karaoke_avatar_registration,
        content_types=['photo'],
        state=[NewKaraoke.avatar, NewKaraoke.edit_avatar]
    )

    dp.register_message_handler(
        karaoke_avatar_is_invalid,
        content_types='any',
        state=[NewKaraoke.avatar, NewKaraoke.edit_avatar]
    )

    dp.register_message_handler(
        karaoke_description_registration,
        lambda message: len(message.text) <= 500,
        state=[NewKaraoke.description, NewKaraoke.edit_description]
    )

    dp.register_message_handler(
        karaoke_description_is_invalid,
        content_types='any',
        state=[NewKaraoke.description, NewKaraoke.edit_description]
    )

    dp.register_callback_query_handler(callback_new_karaoke, Text(startswith='new_karaoke'), state='*')
