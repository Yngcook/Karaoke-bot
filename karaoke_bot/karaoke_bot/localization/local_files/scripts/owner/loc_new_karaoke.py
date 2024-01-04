local_dict = {
    'new_karaoke_command': {
        'messages': {
            'new_name': {
                'en': f"Come up with a <b>NAME</b> for your karaoke.\n\n"
                      f"To make it easier for users to find you, "
                      f"you can come up with a <b>NAME</b> similar to your establishment.",

                'ru': f"Придумайте <b>ИМЯ</b> для вашего караоке.\n\n"
                      f"Чтобы пользователям было легче вас найти, "
                      f"вы можете придумать <b>ИМЯ</b>, похожее на ваше заведение."

            }
        }
    },

    'karaoke_name_registration': {
        'messages': {
            'now_send_photo': {
                'en': "Now send the 🖼 <b>PHOTO</b> you want to set as your karaoke avatar.",
                'ru': "Теперь отправьте 🖼 <b>ФОТО</b>, которое вы хотите установить в качестве аватара для караоке."
            },
            'success_update': {
                'en': "✅ Success! <b>NAME</b> updated.",
                'ru': "✅ Успех! <b>ИМЯ</b> обновлено."
            },
            'already_taken': {
                'en': "🔒 Sorry, this <b>NAME</b> is already taken.",
                'ru': "🔒 Извините, это <b>ИМЯ</b> уже занято"
            }
        },

        'buttons': {
            'skip': {
                'en': "Skip",
                'ru': "Пропустить"
            }
        }
    },

    'karaoke_name_is_invalid': {
        'messages': {
            'invalid_name': {
                'en': "The <b>NAME</b> must be presented in text and contain't any punctuation marks, "
                      "except for: <b>\"$*&_@\"</b>\n\n"
                      "If you want to stop filling out the questionnaire - send the command - /cancel",
                'ru': "<b>ИМЯ</b> должно быть представлено в виде текста и не содержать знаков препинания, "
                      "кроме: <b>\"$*&_@\"</b>\n\n"
                      "Если вы хотите прекратить заполнение анкеты - отправьте команду - /cancel"
            }
        }
    },

    'karaoke_avatar_registration': {
        'messages': {
            'send_description': {
                'en': "Now come up with 🗒 <b>DESCRIPTION</b> for your karaoke",
                'ru': "Теперь придумайте 🗒 <b>ОПИСАНИЕ</b> для вашего караоке."
            },

            'avatar_updated': {
                'en': "✅ Success! 🖼 <b>AVATAR</b> updated.",
                'ru': '✅ Успешно! 🖼 <b>АВАТАР</b> обновлен.'
            }
        },

        'buttons': {
            'skip': {
                'en': "Skip",
                'ru': "Пропустить"
            }
        }
    },

    'karaoke_avatar_is_invalid': {
        'messages': {
            'invalid_avatar': {
                'en': "It seems you sent something wrong. "
                      "Please send a 🖼 <b>PHOTO</b> to the avatar for your karaoke.\n\n"
                      "If you want to stop filling out the questionnaire - send the command - /cancel",
                'ru': "Кажется, вы отправили что-то не так. "
                      "Пожалуйста, отправьте 🖼 <b>ФОТО</b> на аватар для вашего караоке.\n\n"
                      "Если вы хотите прекратить заполнение анкеты - отправьте команду - /cancel"
            }
        }
    },

    'karaoke_description_registration': {
        'messages': {
            'description_updated': {
                'en': "✅ Success! 🗒 <b>DESCRIPTION</b> updated.",
                'ru': "✅ Успешно! 🗒 <b>ОПИСАНИЕ</b> обновлено."
            }
        }
    },

    'karaoke_description_is_invalid': {
        'messages': {
            'description_invalid': {
                'en': "The maximum length of the 🗒 <b>DESCRIPTION</b> should not exceed 500 characters",
                'ru': "Максимальная длина 🗒 <b>ОПИСАНИЯ</b> не должна превышать 500 символов"
            }
        }
    },

    'new_karaoke_command_confirm': {
        'messages': {
            'confirm': {
                'en': "<b>CONFIRM THE CREATION OF KARAOKE</b>\n\n",
                'ru': "<b>ПОДТВЕРДИТE СОЗДАНИЕ КАРАОКЕ</b>\n\n"
            },

            'name': {
                'en': "<b>NAME</b>: ",
                'ru': "<b>ИМЯ</b>: "
            },

            'description': {
                'en': "\n<b>DESCRIPTION</b>: ",
                'ru': "\n<b>ОПИСАНИЕ</b>: "
            }
        }
    },

    'callback_new_karaoke': {
        'messages': {
            'edit_name': {
                'en': "What <b>NAME</b> would you like for your karaoke?",
                'ru': "Какое <b>ИМЯ</b> вы бы хотели видеть в своем караоке?"
            },

            'edit_avatar': {
                'en': "Attach the 🖼 <b>AVATAR</b> you want",
                'ru': "Прикрепите нужный 🖼 <b>АВАТАР</b>"
            },

            'edit_description': {
                'en': "What 🗒 <b>DESCRIPTION</b> would you like?",
                'ru': "Какое 🗒 <b>ОПИСАНИЕ</b> вам нужно?"
            },

            'skip_avatar': {
                'en': "Now come up with 🗒 <b>DESCRIPTION</b> for your karaoke",
                'ru': "Теперь придумайте 🗒 <b>ОПИСАНИЕ</b> для вашего караоке"
            },

            'cancel_force': {
                'en': "❌ Create karaoke canceled",
                'ru': "❌ Создание караоке отменено"
            }
        },

        'buttons': {
            'skip': {
                'en': "Skip",
                'ru': "Пропустить"
            }
        }
    },

    'register_karaoke': {
        'messages': {
            'success': {
                'en': "✅ Success! You have created your <b>virtual karaoke</b>!",
                'ru': "✅ Успех! Вы создали свое <b>виртуальное караоке</b>!"
            },

            'fail': {
                'en': "Oops, something went wrong, we are already working on the error",
                'ru': "Упс, что-то пошло не так, мы уже работаем над ошибкой."
            }
        }
    },

    'keyboard_confirm': {
        'buttons': [
            {
                'en': "✅ Confirm and Create",
                'ru': "✅ Подтвердить и создать",
                'attach_mode': 'add',
                'callback_data': 'new_karaoke create'
            },
            {
                'en': "✏️ Edit",
                'ru': "✏️ Редактировать",
                'attach_mode': 'insert',
                'callback_data': 'new_karaoke edit'
            },
            {
                'en': "❌ Cancel",
                'ru': "❌ Отмена",
                'attach_mode': 'add',
                'callback_data': 'new_karaoke cancel'
            }

        ]
    },

    'keyboard_edit': {
        'buttons': [
            {
                'en': "💬 Edit name",
                'ru': "💬 Изменить имя",
                'attach_mode': 'add',
                'callback_data': 'new_karaoke edit name'
            },
            {
                'en': "🖼 Edit avatar",
                'ru': "🖼 Изменить аватар",
                'attach_mode': 'insert',
                'callback_data': 'new_karaoke edit avatar'
            },
            {
                'en': "🗒 Edit description",
                'ru': "🗒 Изменить описание",
                'attach_mode': 'add',
                'callback_data': 'new_karaoke edit description'
            },
            {
                'en': "<< Back",
                'ru': "<< Назад",
                'attach_mode': 'add',
                'callback_data': 'new_karaoke back'
            }
        ]
    },

    'keyboard_back_to': {
        'buttons': [
            {
                'en': "<< Back to confirmation",
                'ru': "<< Назад к подтверждению",
                'attach_mode': 'add',
                'callback_data': 'new_karaoke back confirmation'
            },
            {
                'en': "<< Back to editing",
                'ru': "<< Назад к редактированию",
                'attach_mode': 'insert',
                'callback_data': 'new_karaoke back editing'
            }
        ]
    },

    'keyboard_create': {
        'buttons': [
            {
                'en': "✅ Create",
                'ru': "✅ Создать",
                'attach_mode': 'add',
                'callback_data': 'new_karaoke create force'
            },
            {
                'en': "<< Back",
                'ru': "<< Назад",
                'attach_mode': 'insert',
                'callback_data': 'new_karaoke back'
            }
        ]
    },

    'keyboard_cancel': {
        'buttons': [
            {
                'en': "❌ Cancel",
                'ru': "❌ Отмена",
                'attach_mode': 'add',
                'callback_data': 'new_karaoke cancel force'
            },
            {
                'en': "<< Back",
                'ru': "<< Назад",
                'attach_mode': 'insert',
                'callback_data': 'new_karaoke back'
            }
        ]
    }
}