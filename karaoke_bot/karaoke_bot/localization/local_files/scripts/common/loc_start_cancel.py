local_dict = {
    'start_command': {
        'messages': {
            'hello_text': {
                'en': """
                Hello, I'm <b>Moloko</b> - karaoke bot. 
                I can help you create and manage virtual karaoke and order tracks to your karaoke-man (person responsible for turning on the music).
                """,

                'ru': """
                Привет, я <b>Moloko</b> — караоке-бот.
                Я могу помочь вам создать и управлять виртуальным караоке, а также заказать треки вашему караоке-мену (человеку, ответственному за включение музыки).
                """
            },

            'start_text': {
                'en': """
                Hello, I'm <b>Moloko</b> - karaoke bot.
                I can help you create and manage virtual karaoke and order tracks to your karaoke-man (person responsible for turning on the music).
                
                You can control me by sending these commands:
                
                /new_karaoke - create a new karaoke
                /search_karaoke - search for karaoke among existing ones
                /menu - show the menu
                /cancel - cancel any action
                
                <b>For users</b>
                /order_track - order a music track
                /show_my_orders - show my current orders
                
                <b>For karaoke owners</b>
                /show_queue - show a queue of tracks in karaoke
                /get_lap_queue - get queue split in laps
                """,

                'ru': "Привет, я <b>Moloko</b> — караоке-бот.\n"
                      "Я могу помочь вам создать и управлять виртуальным караоке, а также заказать треки вашему караоке-мену (человеку, ответственному за включение музыки).\n"
                      "\n"
                      "Вы можете управлять мной, отправив эти команды:\n"
                      "\n"
                      "/new_karaoke — создать новое караоке\n"
                      "/search_karaoke — поиск караоке среди существующих\n"
                      "/menu — показать меню\n"
                      "/cancel — отменить любое действие\n"
                      "\n"
                      "<b>Для пользователей</b>\n"
                      "/order_track - заказать музыкальный трек\n"
                      "/show_my_orders — показать мои текущие заказы\n"
                      "\n"
                      "<b>Для владельцев караоке</b>\n"
                      "/show_queue — показать очередь треков в караоке\n"
                      "/get_lap_queue — разделить очередь по кругам\n"
            },
        }
    },

    'keyboard_start': {
        'buttons': [
            {
                'en': "Order a track",
                'ru': "Заказать трек",
                'attach_mode': 'add'
            },
            {
                'en': "Menu",
                'ru': "Меню",
                'attach_mode': 'add'
            },
            {
                'en': "Cancel",
                'ru': "Отмена",
                'attach_mode': 'insert'
            }
        ]
    }
}
