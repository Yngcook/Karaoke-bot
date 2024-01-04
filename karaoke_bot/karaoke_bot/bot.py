from aiogram.utils import executor
from create_bot import dispatcher
from karaoke_bot.handlers.scripts import admin, moderator, owner, visitor, common


common.start_cancel.register_handlers(dispatcher)
common.menu.register_handlers(dispatcher)

owner.new_karaoke.register_handlers(dispatcher)
owner.queue.register_handlers(dispatcher)
owner.generate_qr_code.register_handlers(dispatcher)


visitor.search_karaoke.register_handlers(dispatcher)
visitor.order_track.register_handlers(dispatcher)
visitor.change_selected_karaoke.register_handlers(dispatcher)
visitor.show_my_orders.register_handlers(dispatcher)

executor.start_polling(dispatcher, skip_updates=True)
