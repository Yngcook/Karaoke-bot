from aiogram import types, Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from karaoke_bot.handlers.scripts.visitor.search_karaoke import search_karaoke
from karaoke_bot.handlers.scripts.common.register_telegram_user import register_telegram_user
from karaoke_bot.localization.localization_manager import LocalizationManager
from karaoke_bot.localization.local_files.scripts.common.loc_start_cancel import local_dict
from karaoke_bot.keyboards.keyboard_factory import KeyboardFactory


lm = LocalizationManager(local_dict=local_dict)
kf = KeyboardFactory(lm=lm)


async def start_command(message: types.Message, state: FSMContext):
    fname = start_command.__name__
    lg_code = message.from_user.language_code

    await register_telegram_user(message.from_user)

    args = message.get_args()
    if args is not None and args != '':  # если команда /start получена по внешней ссылке через QR code

        args = args.split('-')  # смотри delimeter внутри owner.generate_qr_code

        parameters = {}
        for arg in args:
            key, value = arg.split('=')
            parameters[key] = value

        match parameters.get('func'):
            case 'search_karaoke':
                karaoke_name = parameters.get('karaoke_name')
                if karaoke_name is not None:
                    message.text = karaoke_name
                    await message.answer(
                        text=lm.localize_text(fname, lg_code, params=['messages', 'helo_text']),
                        reply_markup=kf.get_reply_keyboard('keyboard_start', lg_code),
                        parse_mode='HTML'
                    )
                    await search_karaoke(message=message, state=state)
    else:
        await message.answer(
            text=lm.localize_text(fname, lg_code, params=['messages', 'start_text']),
            reply_markup=kf.get_reply_keyboard('keyboard_start', lg_code),
            parse_mode='HTML'
        )


async def cancel_command(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Ok")
        return None
    await state.finish()
    await message.reply("Ok")


async def callback_cancel_command(callback: types.CallbackQuery, state: FSMContext):
    await callback.answer()
    await cancel_command(callback.message, state)


def register_handlers(dispatcher: Dispatcher):

    dispatcher.register_callback_query_handler(callback_cancel_command, Text(equals='cancel'))
    dispatcher.register_message_handler(cancel_command, Text(equals=["cancel", "отмена"], ignore_case=True), state='*')
    dispatcher.register_message_handler(cancel_command, commands=['cancel'], state='*')

    dispatcher.register_message_handler(start_command, commands=['start', 'help'], state='*')
