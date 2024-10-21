from telebot import TeleBot
from bot_service.commands import register_commands
from bot_service.handlers import *
from bot_service import TOKEN


bot = TeleBot(TOKEN)
register_commands(bot)
register_hendlears(bot)
register_buttons(bot)

# Start polling
print("Bot is polling...")
bot.polling(none_stop=True)
