from karaoke_bot.localization.localization_manager import LocalizationManager
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


class KeyboardFactory:
    def __init__(self, lm: LocalizationManager):
        self.lm = lm

    def get_reply_keyboard(self, keyboard_name: str, lg_code: str = 'en'):
        buttons_dict = self.lm.get_local_obj(obj_name=keyboard_name, keys=['buttons'])

        if buttons_dict is not None:
            keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
            for button_dict in buttons_dict:
                button_text = button_dict[lg_code]

                if button_dict['attach_mode'] == 'add':
                    keyboard.add(KeyboardButton(button_text))
                else:
                    keyboard.insert(KeyboardButton(button_text))

            return keyboard

        raise KeyError(f"{keyboard_name} does not have keys=['buttons']")

    def get_inline_keyboard(self, keyboard_name: str, lg_code: str = 'en', callbacks_data: dict[int, str] | None = None):
        buttons_dict = self.lm.get_local_obj(obj_name=keyboard_name, keys=['buttons'])

        if buttons_dict is not None:
            keyboard = InlineKeyboardMarkup()
            for idx, button_dict in enumerate(buttons_dict, start=1):
                button_text = button_dict[lg_code]

                if callbacks_data is None:
                    callback_data = button_dict.get('callback_data')
                else:
                    callback_data = callbacks_data.get(idx)
                    if callback_data is None:
                        callback_data = button_dict.get('callback_data')

                if button_dict['attach_mode'] == 'add':
                    keyboard.add(InlineKeyboardButton(text=button_text, callback_data=callback_data))
                else:
                    keyboard.insert(InlineKeyboardButton(text=button_text, callback_data=callback_data))

            return keyboard

        raise KeyError(f"{keyboard_name} does not have keys=['buttons']")
