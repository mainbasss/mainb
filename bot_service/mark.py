from telebot import types

class Mark():
    def __init__(self):
        pass
    def cancel(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
        item1 = types.KeyboardButton('🚫 Отмена')
        markup.add(item1)
        return markup
    def start_markup(self, chat_id):
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        inline_markup.add(types.InlineKeyboardButton(text = "🟢Добавить канал для постов", callback_data="channel_poluch_add"))
        inline_markup.add(types.InlineKeyboardButton(text = "🧬Каналы", callback_data="channel_get"))
        return inline_markup
    def chat_mark(self):
        markup = types.ReplyKeyboardMarkup(resize_keyboard= True)
        markup.add(types.KeyboardButton("❇️Выбрать канал",
                                  request_chat=types.KeyboardButtonRequestChat(request_id=1, chat_is_channel=True)))
        markup.add(types.KeyboardButton('🚫 Отмена'))
        return markup
    def all_channels(self, channels):
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        for ch in channels:
            inline_markup.add(types.InlineKeyboardButton(text = ch[1], callback_data=f"detail_{ch[0]}"))
        inline_markup.add(types.InlineKeyboardButton(text = '⬅️Назад', callback_data="main"))
        return inline_markup
    def channel_info(self, channel_id):
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        inline_markup.add(types.InlineKeyboardButton(text = f'🔮Доноры', callback_data=f"getdonors_{channel_id}"))
        inline_markup.add(types.InlineKeyboardButton(text = f'👁Накрутка просмотров', callback_data=f"prosmotri_{channel_id}"))
        inline_markup.add(types.InlineKeyboardButton(text = '❌Удалить', callback_data=f"delchannel_{channel_id}"))
        inline_markup.add(types.InlineKeyboardButton(text = '⬅️Назад', callback_data="channel_get"))
        return inline_markup
    def prosmotri_diapazon(self, channel_id, diapazon):
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        if diapazon[0]:
            inline_markup.add(types.InlineKeyboardButton(text = f'✏️ Изменить диапазон', callback_data=f"prosmotriEdit_{channel_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = f'❌ Убрать накрутку', callback_data=f"prosmotriDel_{channel_id}"))
        else:
            inline_markup.add(types.InlineKeyboardButton(text = f'✏️ Добавить диапазон', callback_data=f"prosmotriEdit_{channel_id}"))
        inline_markup.add(types.InlineKeyboardButton(text = '⬅️Назад', callback_data=f"detail_{channel_id}"))
        return inline_markup
    def donorOptionsLimitMarkup(self, channel_id, donor_id, info):
        if not info[0]:
            count = 'Не установлено'
            period = 'Не установлен'
        else:
            count = info[0]
            period = info[1]
        markup = types.InlineKeyboardMarkup(row_width=6)
        markup.add(types.InlineKeyboardButton(text='Число постов', callback_data='donorOptionsLimitpass'))
        if info[0]:
            markup.add(types.InlineKeyboardButton(text='➖', callback_data=f'donorOptionsLimitCountDec_{donor_id}_{channel_id}'),
                        types.InlineKeyboardButton(text=count, callback_data='donorOptionsLimitpass'),
                        types.InlineKeyboardButton(text='➕', callback_data=f'donorOptionsLimitCountInc_{donor_id}_{channel_id}'))
        else:
            markup.add(
                        types.InlineKeyboardButton(text=count, callback_data='donorOptionsLimitpass'),
                        types.InlineKeyboardButton(text='➕', callback_data=f'donorOptionsLimitCountInc_{donor_id}_{channel_id}'))
        markup.add(types.InlineKeyboardButton(text='Период', callback_data='donorOptionsLimitpass'))
        markup.add(types.InlineKeyboardButton(text='◀️', callback_data=f'donorOptionsLimitPeriod_{donor_id}_{channel_id}'),
                    types.InlineKeyboardButton(text=period, callback_data='donorOptionsLimitpass'),
                    types.InlineKeyboardButton(text='▶️', callback_data=f'donorOptionsLimitPeriod_{donor_id}_{channel_id}'))
        if info[0]:
            markup.add(types.InlineKeyboardButton(text = '❌Убрать ограничения', callback_data=f"donorOptionsLimitDel_{donor_id}_{channel_id}"))
        markup.add(types.InlineKeyboardButton(text = '⬅️Назад', callback_data=f"donorinfo_{donor_id}_{channel_id}"))
        return markup
