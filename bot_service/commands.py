from bot_service import mark
from bot_service.handlers import update_state, START  # Импортируем функции для управления состоянием
def register_commands(bot):
    @bot.message_handler(commands=['start'])
    def start_message(message):
        '''Отправляет приветственное сообщение на команду start'''
        if message.chat.type == 'private':
            #base.regestry(message.chat.id)
            update_state(message.chat.id, START)
            bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            bot.send_message(message.chat.id, "Добрый день", reply_markup = mark.start_markup(message.chat.id))
