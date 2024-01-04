local_dict = {
    'search_karaoke_command': {
        'messages': {
            'enter_name': {
                'en': f"Enter the <b>NAME</b> of the virtual karaoke where you plan to perform.",
                'ru': "Введите <b>ИМЯ</b> виртуального караоке, в котором вы планируете выступать."
            }
        }
    },

    'search_karaoke': {
        'messages': {
            'no_karaoke': {
                'en': "Oops, there is no such karaoke yet.\n\n"
                      "Try to get the <b>NAME</b> from the administrator of the institution where you are.",
                'ru': "Упс, такого караоке пока нет.\n\n"
                      "Попробуйте узнать <b>ИМЯ</b> у администратора заведения, в котором вы находитесь."
            },

            'karaoke': {
                'en': "<b>Karaoke</b>:",
                'ru': "<b>Караоке</b>: "
            },

            'owner': {
                'en': "<b>Owner</b>:",
                'ru': "<b>Владелец</b>:"
            },

            'subscribers': {
                'en': "<b>Subscribers</b>:",
                'ru': "<b>Подписчиков</b>:"
            },

            'already_sub': {
                'en': "\n\n✅ You have already subscribed!",
                'ru': "\n\n✅ Вы уже подписались!"
            }
        }
    },

    'callback_subscribe_to_karaoke': {
        'messages': {
            'you_sub': {
                'en': "✅ Success! You have subscribed!",
                'ru': "✅ Успех! Вы подписались!"
            }
        }
    },

    'keyboard_order_track': {
        'buttons': [
            {
                'en': "Order a track",
                'ru': "Заказать трек",
                'attach_mode': 'add',
                'callback_data': 'order_track'
            }
        ]
    },

    'keyboard_subscribe': {
        'buttons': [
            {
                'en': "Subscribe",
                'ru': "Подписаться",
                'attach_mode': 'add'
            }
        ]
    },

    'keyboard_already_sub': {
        'buttons': [
            {
                'en': "Order a track",
                'ru': "Заказать трек",
                'attach_mode': 'insert',
                'callback_data': 'order_track'
            },
            {
                'en': "Get QR-code",
                'ru': "Получить QR код",
                'attach_mode': 'insert'
            }
        ]
    }
}