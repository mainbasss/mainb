# bot_service/handlers.py
from collections import defaultdict
from telebot import types
from telebot.apihelper import ApiTelegramException
import traceback
from bot_service import *
from parser_service.gpt import gpt_message
from Promotion import promotion_manger

START, POLUCH, DONOR, NAKRUTKA = range(4)

USER_STATE = defaultdict(lambda: START)

def update_state(chat_id, state):
    '''Изменить состояние пользователя'''
    USER_STATE[chat_id] = state

def get_state(chat_id):
    '''Получить текущее состояние пользователя'''
    return USER_STATE[chat_id]

def is_admin(bot_id, chat, bot):
    try:
        admins = bot.get_chat_administrators(chat)
        for admin in admins:
            if admin.user.id == bot_id:
                return True
        return False
    except ApiTelegramException:
        return False

def register_hendlears(bot):
    @bot.message_handler(content_types=['chat_shared'])
    def handle_shared_chat(message):

        chat = message.chat_shared.chat_id
        chat_id = message.chat.id
        bot.delete_message(chat_id=chat_id, message_id=message.message_id)
        bot.delete_message(chat_id=chat_id, message_id=message.message_id-1)
        if is_admin(chat_id, chat, bot):
            chat_info = bot.get_chat(chat)

            if get_state(chat_id) == POLUCH:
                res = channel_instance.add(chat_id, chat, chat_info.title, chat_info.username)
                if res:
                    inline_markup = types.InlineKeyboardMarkup(row_width=2)
                    inline_markup.add(types.InlineKeyboardButton(text = "Да", callback_data=f"addeyes_{chat}"),types.InlineKeyboardButton(text = "Нет", callback_data="addeno"))
                    bot.send_message(chat_id, "Канал добавлен\nХотите добавить канал донор?", reply_markup = inline_markup)
                    update_state(chat_id, START)
                else:
                    bot.send_message(chat_id, "Канал уже есть", reply_markup = mark.chat_mark())
            elif get_state(chat_id) == DONOR:
                res = donor_instance.add(chat_id, chat, chat_info.title, chat_info.username)
                if res:
                    donors = donor_instance.get_donors(res)
                    inline_markup = types.InlineKeyboardMarkup(row_width=2)
                    for donor in donors:
                        inline_markup.add(types.InlineKeyboardButton(text = donor[1], callback_data=f"donorinfo_{donor[0]}"))
                    inline_markup.add(types.InlineKeyboardButton(text = '❇️Добавить донора', callback_data=f"addeyes_{res}"))
                    inline_markup.add(types.InlineKeyboardButton(text = '⬅️Назад', callback_data=f"detail_{res}"))
                    info = channel_instance.get_info(res)
                    bot.send_message(chat_id, f"Доноры канала <b>{info[0]}</>", reply_markup = inline_markup, parse_mode='HTML')
                    update_state(chat_id, START)
                else:
                    bot.send_message(chat_id, "Канал уже есть", reply_markup = mark.chat_mark())


        else:
            bot.send_message(message.chat.id, "Сделайте бота администратором в канала!", reply_markup = mark.chat_mark())
    #NAKRUTKA
    @bot.message_handler(func=lambda message: get_state(message.chat.id) == NAKRUTKA)
    def nakrutka_handler(message):
        chat_id = message.chat.id
        text = message.text
        if text == "🚫 Отмена":
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            except:
                pass
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
            except:
                pass
            remove_markup = types.ReplyKeyboardRemove()
            messs = bot.send_message(message.chat.id, "1", reply_markup=remove_markup)
            bot.delete_message(chat_id=messs.chat.id, message_id=messs.message_id)
            markup = mark.start_markup(chat_id)
            bot.send_message(chat_id, "Вы отменили ввод данных", reply_markup = markup)
            channel_instance.del_status(chat_id)
            update_state(chat_id, START)
        else:
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
            except:
                pass
            try:
                bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
            except:
                pass
            while True:
                if ' ' in text:
                    text = text.replace(' ', '')
                else:
                    break
            if text.isdigit():
                text = message.text
                # Разделяем строку по пробелам и фильтруем пустые строки
                parts = list(filter(None, text.split()))
                # Объединяем обратно с одним пробелом
                result_string = ' '.join(parts[:2])
                if not ' ' in result_string:
                    bot.send_message(chat_id, "Вы ввели одно число. Нудно два.")
                elif int(result_string.split(' ')[0]) < 10 or int(result_string.split(' ')[1]) < 10:
                    bot.send_message(chat_id, "Минимальное число просмотров должно быть больше 10")
                elif int(result_string.split(' ')[0]) >= int(result_string.split(' ')[1]):
                    bot.send_message(chat_id, "Первое число должно быть меньше второго")
                else:
                    channel_id = channel_instance.update_prosmotri_diapazon(chat_id, result_string)
                    inline_markup = types.InlineKeyboardMarkup(row_width=2)
                    inline_markup.add(types.InlineKeyboardButton(text = '⬅️Назад', callback_data=f"detail_{channel_id}"))
                    bot.send_message(chat_id, f"Диапазон <b>{result_string.replace(' ',' - ')}</> просмотров успешно добавлен", reply_markup = inline_markup, parse_mode='HTML')
                    update_state(chat_id, START)
            else:
                bot.send_message(chat_id, "Допустимы только целые числа")
    @bot.message_handler(func=lambda message: True, content_types=[
        'text', 'photo', 'audio', 'document', 'video',
        'animation', 'voice', 'video_note', 'location',
        'contact', 'poll', 'dice', 'invoice', 'successful_payment'
    ])
    def get_text_messages(message):
            chat_id = message.chat.id
            if message.forward_from_chat:
                chat_id = message.chat.id
                chat = message.forward_from_chat.id
                bot.delete_message(chat_id=chat_id, message_id=message.message_id)
                try:
                    bot.delete_message(chat_id=chat_id, message_id=message.message_id-1)
                except:
                    pass
                chat_info = message.forward_from_chat
                if not chat_info.username:
                    bot.send_message(chat_id, "Канал закрыт", reply_markup=mark.start_markup(chat_id))
                    channel_instance.del_status(chat_id)
                    update_state(chat_id, START)  # Измените состояние на START
                else:
                    if get_state(chat_id) == POLUCH:
                        if is_admin(bot.get_me().id, chat, bot):  # Убедитесь, что используете ID бота
                            res = channel_instance.add(chat_id, chat, chat_info.title, chat_info.username)
                            if res:
                                inline_markup = types.InlineKeyboardMarkup(row_width=2)
                                inline_markup.add(types.InlineKeyboardButton(text="Да", callback_data=f"addeyes_{chat}"),
                                                   types.InlineKeyboardButton(text="Нет", callback_data="addeno"))
                                bot.send_message(chat_id, "Канал добавлен\nХотите добавить канал донор?", reply_markup=inline_markup)
                                update_state(chat_id, START)  # Измените состояние на START
                            else:
                                bot.send_message(chat_id, "Канал уже есть", reply_markup=mark.chat_mark())
                        else:
                            bot.send_message(chat_id, "Сделайте бота администратором в канале!", reply_markup=mark.chat_mark())
                    elif get_state(chat_id) == DONOR:
                        try:
                            res = donor_instance.add(chat_id, chat, chat_info.title, chat_info.username)
                            if res:
                                print('res',res)
                                donors = donor_instance.get_donors(res)
                                print('donors',donors)
                                inline_markup = types.InlineKeyboardMarkup(row_width=2)
                                for donor in donors:
                                    inline_markup.add(types.InlineKeyboardButton(text=donor[1], callback_data=f"donorinfo_{donor[0]}_{res}"))
                                inline_markup.add(types.InlineKeyboardButton(text='❇️Добавить донора', callback_data=f"addeyes_{res}"))
                                inline_markup.add(types.InlineKeyboardButton(text='⬅️Назад', callback_data=f"detail_{res}"))
                                info = channel_instance.get_info(res)
                                print('info',info)
                                bot.send_message(chat_id, f"Донор <b>{chat_info.title}</> для канала <b>{info[0]}</> успешно добавлен\nДоноры канала <b>{info[0]}</>", reply_markup=inline_markup, parse_mode='HTML')
                                update_state(chat_id, START)  # Измените состояние на START
                            else:
                                bot.send_message(chat_id, "Канал уже есть", reply_markup=mark.chat_mark())
                        except Exception as e:
                            print(traceback.format_exc())

            if message.chat.type == 'private':
                text = message.text
                chat_id = message.chat.id
                if text == "🚫 Отмена":
                    try:
                        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
                    except:
                        pass
                    try:
                        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
                    except:
                        pass
                    remove_markup = types.ReplyKeyboardRemove()
                    messs = bot.send_message(message.chat.id, "1", reply_markup=remove_markup)
                    bot.delete_message(chat_id=messs.chat.id, message_id=messs.message_id)
                    markup = mark.start_markup(chat_id)
                    bot.send_message(chat_id, "Вы отменили ввод данных", reply_markup=markup)
                    channel_instance.del_status(chat_id)
                    update_state(chat_id, START)

#Кнопки
def register_buttons(bot):
    #Donor Options
    @bot.callback_query_handler(func=lambda call: 'donorOptions' in call.data)
    def handle_callback_query(call):
        text = call.data
        if text == 'donorOptionsLimitpass':
            return
        chat_id = call.message.chat.id
        print('из donorOptions', text)
        donor_id = int(text.split('_')[1])
        channel_id = int(text.split('_')[2])
        info = donor_instance.get_limits(donor_id, channel_id)
        message_text = (
            'Здесь вы можете настроить лимит входящих сообщений'
            )
        if 'CountDec' in text:
            info = donor_instance.update_limits(donor_id, channel_id, 'CountDec', info)
        elif 'CountInc' in text:
            info = donor_instance.update_limits(donor_id, channel_id, 'CountInc', info)
        elif 'Period' in text:
            info = donor_instance.update_limits(donor_id, channel_id, 'Period', info)
        elif 'Del' in text:
            info = donor_instance.update_limits(donor_id, channel_id, 'Del', info)

        if not info[0] and not info[1]:
            dop = '\n\n<b>Сейчас лимит не утановлен</>'
        elif info[0]:
            dop = f'\n\nТекущий лимит: <b>{info[0]} в {info[1]}</>'


        if 'CountDec' in text or 'CountInc' in text or 'Period' in text or 'Del' in text:
            try:
                bot.edit_message_text(message_text+dop,
                                chat_id,
                                call.message.message_id,
                                reply_markup = mark.donorOptionsLimitMarkup(
                                                                            channel_id,
                                                                            donor_id,
                                                                            info),
                                parse_mode = 'HTML')
            except:
                pass
        elif 'donorOptionsLimit' in text:
            bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)

            bot.send_message(chat_id,
                            message_text+dop,
                            reply_markup = mark.donorOptionsLimitMarkup(
                                                                        channel_id,
                                                                        donor_id,
                                                                        info),
                            parse_mode = 'HTML')
    #FIRST
    @bot.callback_query_handler(func=lambda call: 'first' in call.data)
    def handle_callback_query(call):
        text = call.data
        print('из first',text)
        chat_id = call.message.chat.id
        if 'media' in text:
            media = True
            grouped_id = call.data.split('_')[3].replace('media','')
        else:
            media = False
            grouped_id = None
        if 'refuse' in text:
            bot.answer_callback_query(call.id, "Пост отклонен")
            bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
            if media:
                n = media_group_instance.delete(grouped_id)
                for i in range(1, n+1):
                    bot.delete_message(chat_id=chat_id, message_id=call.message.message_id-i)
        elif 'confirm' in text:
            channel_id = int(text.split('_')[2])
            donor_info = donor_instance.get_info(channel_id)
            channel = donor_info[0]
            name = donor_info[1]
            donor_name, channelels = channel_instance.get_name(channel_id)
            str_channelels = ', @'.join(channelels)
            inline_markup = types.InlineKeyboardMarkup(row_width=2)
            inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"second_confirm_{channel_id}"),
                    types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"second_refuse_{channel_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"second_edit_{channel_id}"))
            bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
            m = bot.send_message(chat_id, 'Ожидайте...')
            # Если сообщение содержит фото
            if call.message.photo or call.message.video:
                message_text = call.message.caption.split(name+'\n')[1].split('\n\nК данному источнику(')[0]
                while True:
                    print('Я в ЧАТЕ ЖэПэТэ')
                    message_text_pre = gpt_message(message_text)
                    if ('<li>' in message_text_pre or
                        '<h2>'  in message_text_pre or
                        '<p>'  in message_text_pre or
                        '<ul>'  in message_text_pre):
                        continue
                    else:
                        message_text = message_text_pre
                        break
                message_text = (
                        f'<i>🖋 Рерайт поста от</> <b>ChatGPT</> для канала <code>{donor_name}</>:\n\n'
                        f'{message_text}\n\n'
                        f'<b>К данному источнику(<code>{donor_name}</>) привязанные данный(ые) канал(ы): @{str_channelels}</>'
                        )
                bot.delete_message(chat_id=chat_id, message_id=m.message_id)
                if call.message.photo:
                    file = call.message.photo[-1].file_id
                    bot.send_photo(chat_id=chat_id, photo=file, caption=message_text, reply_markup = inline_markup, parse_mode='HTML')
                # Если сообщение содержит видео
                elif call.message.video:
                    file = call.message.video.file_id
                    bot.send_video(chat_id=chat_id, video=file, caption=message_text, reply_markup=inline_markup, parse_mode='HTML')
            else:
                if media:
                    media_files, n = media_group_instance.get(grouped_id)
                    for i in range(1, n+1):
                        bot.delete_message(chat_id=chat_id, message_id=call.message.message_id-i)
                message_text = call.message.text.split(name+'\n')[1].split('\n\nК данному источнику(')[0]
                while True:
                    message_text_pre = gpt_message(message_text)
                    if ('<li>' in message_text_pre or
                        '<h2>'  in message_text_pre or
                        '<p>'  in message_text_pre or
                        '<ul>'  in message_text_pre):
                        continue
                    else:
                        message_text = message_text_pre
                        break
                bot.delete_message(chat_id=chat_id, message_id=m.message_id)
                message_text = (
                        f'<i>🖋 Рерайт поста от</> <b>ChatGPT</> для канала <code>{donor_name}</>:\n\n'
                        f'{message_text}\n\n'
                        f'<b>К данному источнику(<code>{donor_name}</>) привязанные данный(ые) канал(ы): @{str_channelels}</>'
                        )
                if media:
                    bot.send_media_group(chat_id=chat_id, media=media_files)
                    inline_markup = types.InlineKeyboardMarkup(row_width=2)
                    inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"second_confirm_{channel_id}_media{grouped_id}"),
                            types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"second_refuse_{channel_id}_media{grouped_id}"))
                    inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"second_edit_{channel_id}_media{grouped_id}"))
                bot.send_message(chat_id, message_text, reply_markup = inline_markup, parse_mode='HTML')

        elif 'edit' in text:
            channel_id = int(text.split('_')[2])
            markup = types.InlineKeyboardMarkup()
            donor_info = donor_instance.get_info(channel_id)
            channel = donor_info[0]
            name = donor_info[1]
            if call.message.photo or call.message.video:
                message_text = call.message.caption.split(name+'\n')[1].split('\n\nК данному источнику(')[0]
            else:
                message_text = call.message.text.split(name+'\n')[1].split('\n\nК данному источнику(')[0]
            confirm_button = types.InlineKeyboardButton("✅Редактировать",switch_inline_query_current_chat=message_text)
            if media:
                cancel_button = types.InlineKeyboardButton("❌Отменить", callback_data=f"first_cancel_{channel_id}_media{grouped_id}")
            else:
                cancel_button = types.InlineKeyboardButton("❌Отменить", callback_data=f"first_cancel_{channel_id}")
            markup.add(confirm_button, cancel_button)
            bot.edit_message_reply_markup(call.message.chat.id, message_id = call.message.message_id, reply_markup = markup)
            bot.register_next_step_handler(call.message, process_first_edit, channel_id = channel_id, mess_id = call.message.message_id, channel=channel, mess=call.message, grouped_id=grouped_id)
        elif 'cancel' in text:
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            channel_id = int(text.split('_')[2])
            inline_markup = types.InlineKeyboardMarkup()
            if media:
                inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"first_confirm_{channel_id}_media{grouped_id}"),
                        types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"first_refuse_{channel_id}_media{grouped_id}"))
                inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"first_edit_{channel_id}_media{grouped_id}"))
            else:
                inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"first_confirm_{channel_id}"),
                        types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"first_refuse_{channel_id}"))
                inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"first_edit_{channel_id}"))
            bot.edit_message_reply_markup(call.message.chat.id, message_id = call.message.message_id, reply_markup = inline_markup)
    #FIRST
    def process_first_edit(message, **kwargs):
        channel_id = kwargs.get('channel_id')
        mess_id = kwargs.get('mess_id')
        channel = kwargs.get('channel')
        mess = kwargs.get('mess')
        grouped_id = kwargs.get('grouped_id')
        text = message.text
        donor_name, channelels = channel_instance.get_name(channel_id)
        str_channelels = ', @'.join(channelels)
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        if grouped_id:
            inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"second_confirm_{channel_id}_media{grouped_id}"),
                    types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"second_refuse_{channel_id}_media{grouped_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"second_edit_{channel_id}_media{grouped_id}"))
        else:
            inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"second_confirm_{channel_id}"),
                    types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"second_refuse_{channel_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"second_edit_{channel_id}"))
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=message.chat.id, message_id=mess_id)
        while True:
            print('Я в ЧАТЕ ЖэПэТэ')
            message_text_pre = gpt_message(text)
            if ('<li>' in message_text_pre or
                '<h2>'  in message_text_pre or
                '<p>'  in message_text_pre or
                '<ul>'  in message_text_pre):
                continue
            else:
                message_text = message_text_pre
                break
        message_text = (
                f'<i>🖋 Рерайт поста от</> <b>ChatGPT</> для канала <code>{donor_name}</>:\n\n'
                f'{message_text}\n\n'
                f'<b>К данному источнику(<code>{donor_name}</>) привязанные данный(ые) канал(ы): @{str_channelels}</>'
                )
        if mess.photo:
            file = mess.photo[-1].file_id
            bot.send_photo(chat_id=message.chat.id, photo=file, caption=message_text, reply_markup = inline_markup, parse_mode='HTML')
        elif mess.video:
            file = mess.video.file_id
            bot.send_video(chat_id=message.chat.id, video=file, caption=message_text, reply_markup=inline_markup, parse_mode='HTML')
        else:
            if grouped_id:
                media_files, n = media_group_instance.get(grouped_id)
                for i in range(1, n+1):
                    bot.delete_message(chat_id=message.chat.id, message_id=mess_id-i)
                bot.send_media_group(chat_id=message.chat.id, media=media_files)
            bot.send_message(message.chat.id, message_text, reply_markup = inline_markup, parse_mode='HTML')


    #SECOND
    @bot.callback_query_handler(func=lambda call: 'second' in call.data)
    def handle_callback_query(call):
        text = call.data
        print('из second',text)
        chat_id = call.message.chat.id
        if 'media' in text:
            media = True
            grouped_id = call.data.split('_')[3].replace('media','')
        else:
            media = False
            grouped_id = None
        if 'refuse' in text:
            bot.answer_callback_query(call.id, "Пост отклонен")
            bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
            if media:
                n = media_group_instance.delete(grouped_id)
                for i in range(1, n+1):
                    bot.delete_message(chat_id=chat_id, message_id=call.message.message_id-i)
        elif 'confirm' in text:
            channel_id = int(text.split('_')[2])
            donor_info = donor_instance.get_info(channel_id)
            channel = donor_info[0]
            name = donor_info[1]
            if call.message.photo:
                message_text = call.message.caption.split(name+':\n')[1].split('\n\nК данному источнику(')[0]
                file = call.message.photo[-1].file_id
                mess = bot.send_photo(chat_id=channel, photo=file, caption=message_text, parse_mode='HTML')
            elif call.message.video:
                message_text = call.message.caption.split(name+':\n')[1].split('\n\nК данному источнику(')[0]
                file = call.message.video.file_id
                mess = bot.send_video(chat_id=channel, video=file, caption=message_text, parse_mode='HTML')
            else:
                message_text = call.message.text.split(name+':\n')[1].split('\n\nК данному источнику(')[0]
                if media:
                    media_files, n = media_group_instance.get(grouped_id)
                    for i in range(1, n+1):
                        bot.delete_message(chat_id=chat_id, message_id=call.message.message_id-i)
                    media_files[0].caption = message_text  # Добавляем подпись к первому файлу
                    media_files[0].parse_mode = 'HTML'  # Указываем режим для форматирования HTML
                    mess = bot.send_media_group(chat_id=channel, media=media_files)[0]
                    media_group_instance.delete(grouped_id)
                else:
                    mess = bot.send_message(channel, message_text, parse_mode='HTML')
            #diapazon
            diapazon = channel_instance.get_prosmotri_diapazon(channel, chat_id)
            if diapazon:
                link = f"https://t.me/{mess.chat.username}/{mess.message_id}"
                print(link)
                promotion_manger.distribute_views(link, diapazon)
            ######
            bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
            #отправить в GPT
        elif 'edit' in text:
            channel_id = int(text.split('_')[2])
            markup = types.InlineKeyboardMarkup()
            donor_info = donor_instance.get_info(channel_id)
            channel = donor_info[0]
            name = donor_info[1]
            if call.message.photo or call.message.video:
                message_text = call.message.caption.split(name+':\n')[1].split('\nК данному источнику(')[0]
            else:
                message_text = call.message.text.split(name+':\n')[1].split('\nК данному источнику(')[0]
            confirm_button = types.InlineKeyboardButton("✅Редактировать",switch_inline_query_current_chat=message_text)
            if media:
                cancel_button = types.InlineKeyboardButton("❌Отменить", callback_data=f"second_cancel_{channel_id}_media{grouped_id}")
            else:
                cancel_button = types.InlineKeyboardButton("❌Отменить", callback_data=f"second_cancel_{channel_id}")
            markup.add(confirm_button, cancel_button)
            bot.edit_message_reply_markup(call.message.chat.id, message_id = call.message.message_id, reply_markup = markup)
            bot.register_next_step_handler(call.message, process_second_edit, channel_id = channel_id, mess_id = call.message.message_id, channel=channel, mess=call.message, grouped_id=grouped_id)
        elif 'cancel' in text:
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            channel_id = int(text.split('_')[2])
            inline_markup = types.InlineKeyboardMarkup()
            if media:
                inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"second_confirm_{channel_id}_media{grouped_id}"),
                        types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"second_refuse_{channel_id}_media{grouped_id}"))
                inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"second_edit_{channel_id}_media{grouped_id}"))
            else:
                inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"second_confirm_{channel_id}"),
                        types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"second_refuse_{channel_id}"))
                inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"second_edit_{channel_id}"))
            bot.edit_message_reply_markup(call.message.chat.id, message_id = call.message.message_id, reply_markup = inline_markup)

    #SECOND
    def process_second_edit(message, **kwargs):
        channel_id = kwargs.get('channel_id')
        mess_id = kwargs.get('mess_id')
        channel = kwargs.get('channel')
        mess = kwargs.get('mess')
        grouped_id = kwargs.get('grouped_id')
        bot_info = bot.get_me()
        bot_username = bot_info.username
        text = message.text.replace(f'@{bot_username}','')
        donor_info = donor_instance.get_info(channel_id)
        channel = donor_info[0]
        name = donor_info[1]
        donor_name, channelels = channel_instance.get_name(channel_id)
        str_channelels = ', @'.join(channelels)
        inline_markup = types.InlineKeyboardMarkup(row_width=2)
        if grouped_id:
            inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"second_confirm_{channel_id}_media{grouped_id}"),
                    types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"second_refuse_{channel_id}_media{grouped_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"second_edit_{channel_id}_media{grouped_id}"))
        else:
            inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"second_confirm_{channel_id}"),
                    types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"second_refuse_{channel_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"second_edit_{channel_id}"))
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.delete_message(chat_id=message.chat.id, message_id=mess_id)
        if mess.photo:
            message_text = (
                    f'<i>🖋 Вы отредактировали пост</> для канала <code>{donor_name}</>:\n\n'
                    f'{text}\n\n'
                    f'<b>К данному источнику(<code>{donor_name}</>) привязанные данный(ые) канал(ы): @{str_channelels}</>'
                    )
            file = mess.photo[-1].file_id
            bot.send_photo(chat_id=message.chat.id, photo=file, caption=message_text, reply_markup = inline_markup, parse_mode='HTML')
        # Если сообщение содержит видео
        elif mess.video:
            message_text = (
                    f'<i>🖋 Вы отредактировали пост</> для канала <code>{donor_name}</>:\n\n'
                    f'{text}\n\n'
                    f'<b>К данному источнику(<code>{donor_name}</>) привязанные данный(ые) канал(ы): @{str_channelels}</>'
                    )
            file = mess.video.file_id
            bot.send_video(chat_id=message.chat.id, video=file, caption=message_text, reply_markup=inline_markup, parse_mode='HTML')
        else:
            message_text = (
                    f'<i>🖋 Вы отредактировали пост</> для канала <code>{donor_name}</>:\n\n'
                    f'{text}\n\n'
                    f'<b>К данному источнику(<code>{donor_name}</>) привязанные данный(ые) канал(ы): @{str_channelels}</>'
                    )
            if grouped_id:
                media_files, n = media_group_instance.get(grouped_id)
                for i in range(1, n+1):
                    bot.delete_message(chat_id=message.chat.id, message_id=mess_id-i)
                bot.send_media_group(chat_id=message.chat.id, media=media_files)
            bot.send_message(message.chat.id, message_text, reply_markup = inline_markup, parse_mode='HTML')


    #Prosmotri
    @bot.callback_query_handler(func=lambda call: 'prosmotri' in call.data)
    def handle_callback_query(call):
        text = call.data
        print('из prosmotri', text)
        chat_id = call.message.chat.id
        channel_id = int(text.split('_')[1])
        bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
        if 'prosmotriEdit' in text:
            text = (
            'Введите количество накрутки просмотров в виде двух целых числ через пробел\n'
            '<b>Пример:</> 15 100'
            )
            bot.send_message(chat_id, text, reply_markup = mark.cancel(), parse_mode = 'HTML')
            channel_instance.update_status(channel_id, 'prosmotri')
            update_state(chat_id,NAKRUTKA)
        elif 'prosmotri' in text:
            if 'prosmotriDel' in text:
                channel_instance.update_status(channel_id, 'prosmotri')
                channel_id = channel_instance.update_prosmotri_diapazon(chat_id, None)
            diapazon = channel_instance.get_prosmotri_diapazon(channel_id, chat_id)
            markup = mark.prosmotri_diapazon(channel_id, diapazon)
            if diapazon:
                diapazon = diapazon.replace(' ', ' - ')
            else:
                diapazon = 'Просмотры не накручиваются'
            text = (
            'Здесь вы можете настроить накрутку просмотров на новые посты в ваш канал.\n\n'
            f'Текущий диапазон: <b>{diapazon}</>'
            )
            bot.send_message(chat_id, text, reply_markup = markup, parse_mode = 'HTML')


    @bot.callback_query_handler(func=lambda call: True)
    def handle_callback_query(call):
        text = call.data
        print(text)
        chat_id = call.message.chat.id
        bot.delete_message(chat_id=chat_id, message_id=call.message.message_id)
        if text == 'main':
            bot.send_message(chat_id, "Главное меню", reply_markup = mark.start_markup(chat_id))
        elif text == 'channel_poluch_add':
            bot.send_message(chat_id,
            'Давайте добавим канал, в который будем редиректить посты.\n\n'
            '<b>❗️Прежде чем добавлять канал, вы должны добавить этого бота в ваш канал</>\n\n'
            'Выберите канал, нажав на кнопку ниже ❇️ <b>Выбрать канал</b> (доступны только каналы, где бот админ).\n\n'
            'Или перешлите любой пост из канала сюда (доступны только каналы, где бот админ).'
            , reply_markup = mark.chat_mark(), parse_mode = 'HTML')
            update_state(chat_id, POLUCH)
        elif 'adde' in  text:
            if 'yes' in text:
                channel_id = int(text.split('_')[1])
                channel_instance.update_status(channel_id, 'wait')
                bot.send_message(chat_id,
                'Давайте добавим канал, из которого будем редиректить посты.\n\n'
                '<b>❗️Прежде чем добавлять канал, убедитесь что канал открытый, наш сервис не работает с закрытыми '
                'каналами</>\n\n'
                'Выберите канал, нажав на кнопку ниже ❇️ <b>Выбрать канал</b> (доступны только каналы, где бот админ).\n\n'
                'Или перешлите любой пост из канала сюда (поддерживаются любые каналы, даже если бот не админ).'
                , reply_markup = mark.chat_mark(), parse_mode = 'HTML')
                update_state(chat_id, DONOR)
            elif 'no' in text:
                bot.send_message(chat_id, "Главное меню", reply_markup = mark.start_markup(chat_id))
        elif text == 'channel_get':
            channels = channel_instance.get_channels(chat_id)
            if not channels:
                bot.send_message(chat_id, "Вы не добавили ни одного канала", reply_markup = mark.start_markup(chat_id))
            else:
                bot.send_message(chat_id, "Выберите канал⤵️", reply_markup = mark.all_channels(channels))
        elif 'detail_' in text:
            channel_id = int(text.split('_')[1])
            info = channel_instance.get_info(channel_id)
            donors = donor_instance.get_donors(channel_id)
            if donors == []:
                donors = 0
            elif donors:
                donors = len(donors)
            else:
                donors = 0
            bot.send_message(chat_id,
                        f"<b>Название канала:</> {info[0]}\n"
                        f"<b>Username канала:</> @{info[1]}\n"
                        f"<b>Количество доноров:</> {donors}\n"
                        , reply_markup = mark.channel_info(channel_id), parse_mode = 'HTML')
        elif 'delchannel_' in text:
            channel_id = int(text.split('_')[1])
            channel_instance.delete(channel_id)
            channels = channel_instance.get_channels(chat_id)
            if channels:
                bot.send_message(chat_id, "Выберите канал⤵️", reply_markup = mark.all_channels(channels))
            else:
                bot.send_message(chat_id, "Главное меню", reply_markup = mark.start_markup(chat_id))
        elif 'getdonors_' in text or 'deldonor_' in text:
            if 'deldonor_' in text:
                donor_id = int(text.split('_')[1])
                info = donor_instance.get_info(donor_id)
                bot.answer_callback_query(call.id, f"Канал {info[1]} удален")
                channel_id = info[0]
                donor_instance.delete(donor_id)
            else:
                channel_id = int(text.split('_')[1])
            donors = donor_instance.get_donors(channel_id)
            inline_markup = types.InlineKeyboardMarkup(row_width=2)
            for donor in donors:
                inline_markup.add(types.InlineKeyboardButton(text = donor[1], callback_data=f"donorinfo_{donor[0]}_{channel_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = '❇️Добавить донора', callback_data=f"addeyes_{channel_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = '⬅️Назад', callback_data=f"detail_{channel_id}"))
            info = channel_instance.get_info(channel_id)
            bot.send_message(chat_id, f"Доноры канала <b>{info[0]}</>", reply_markup = inline_markup, parse_mode='HTML')


        elif 'donorinfo_' in text:
            donor_id = int(text.split('_')[1])
            channel_id = int(text.split('_')[2])
            info = donor_instance.get_info(donor_id)
            limit_info = donor_instance.get_limits(donor_id, channel_id)
            if not limit_info[0] and not limit_info[1]:
                dop = ' Сейчас лимит не утановлен'
            elif limit_info[0]:
                dop = f' {limit_info[0]} в {limit_info[1]}'
            inline_markup = types.InlineKeyboardMarkup(row_width=2)
            inline_markup.add(types.InlineKeyboardButton(text = '✋Ограничения', callback_data=f"donorOptionsLimit_{donor_id}_{channel_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = '❌Удалить', callback_data=f"deldonor_{donor_id}_{channel_id}"))
            inline_markup.add(types.InlineKeyboardButton(text = '⬅️Назад', callback_data=f"getdonors_{info[0]}"))

            bot.send_message(chat_id,
                    f"<b>Название канала:</> {info[1]}\n"
                    f"<b>Username канала:</> @{info[2]}\n\n"
                    f"<b>Ограничения сообщений:</>{dop}"


                    , reply_markup = inline_markup, parse_mode = 'HTML')
