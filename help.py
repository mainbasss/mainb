import json
import os
from telebot import types
import sqlite3
from datetime import datetime, timedelta
from time import sleep

########
#Работа с файлом
class Files():
    def __init__(self):
        pass
    def add_data(self,key, info, file):
        '''Добавляет данные в фаил'''
        file = str(file) + '.json'
        if os.path.exists('files/'+file):
            with open('files/'+file, encoding='utf-8') as json_file:
                data = json.load(json_file)
        else:
            data = {}
        data[key] = info
        with open('files/'+file, 'w', encoding='utf-8') as outfile:
            json.dump(data, outfile)

    def delete_file(self,file):
        '''Удаляет фаил'''
        file = 'files/' + str(file) + '.json'
        if os.path.exists(file):
            os.remove(file)

    def get_par(self,key, file):
        file = str(file) + '.json'
        if os.path.exists('files/'+file):
            with open('files/'+file, encoding='utf-8') as json_file:
                data = json.load(json_file)
        return data[key]
##########
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


##########
#Data base
class Base():
    def __init__(self):
        folder_name = 'files'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        self.db_file = os.path.join(folder_name, 'base.db')
        if not os.path.exists(self.db_file):
            # Создать файл базы данных
            conn = sqlite3.connect(self.db_file)
            conn.close()
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS channels (
                chat_id INTEGER NOT NULL,
                channel_id INTEGER,
                title TEXT,
                username TEXT,
                status TEXT,
                prosmotri_diapazon TEXT
           )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS donors (
                channel_id INTEGER,
                donor_id INTEGER,
                donor_title TEXT,
                donor_username TEXT,
                limit_count INTEGER,
                limit_period TEXT,
                start_period TEXT,
                send_message_count INTEGER
           )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS media_group (
            grouped_id TEXT,
            message_id INTEGER,
            chat_id INTEGER,
            media_type TEXT,
            file_id TEXT

        )
        ''')
        conn.close()
    #Добавляем канал приемник
    def channel_poluch_add(self, chat_id, channel_id, title, username):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT * FROM channels WHERE channel_id = ?', (channel_id,))
        data = cursor.fetchone()
        if not data:
            sql_query = f"INSERT INTO channels (chat_id, channel_id, title, username) VALUES (?,?,?,?)"
            cursor.execute(sql_query, (chat_id, channel_id, title, username))
            conn.commit()
            conn.close()
            return True
        else:
            conn.close()
            return False
    def channel_poluch_status(self, channel_id, status):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'UPDATE channels SET status = ? WHERE channel_id=?', (status, channel_id))
        conn.commit()
        conn.close()

    #Добавляем канал донор
    def channel_donor_add(self, chat_id, chat, title, username):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT channel_id FROM channels WHERE status = ? AND chat_id = ?', ('wait',chat_id))
        channel_id = cursor.fetchone()[0]
        cursor.execute(f'SELECT * FROM donors WHERE donor_id = ?', (chat,))
        data = cursor.fetchone()
        if not data:
            sql_query = f"INSERT INTO donors (channel_id, donor_id, donor_title, donor_username) VALUES (?,?,?,?)"
            cursor.execute(sql_query, (channel_id, chat, title, username))
            cursor.execute(f'UPDATE channels SET status = ? WHERE channel_id=?', (None, channel_id))
            conn.commit()
            conn.close()
            return channel_id
        else:
            conn.close()
            return False
    def del_status(self, chat_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'UPDATE channels SET status = ? WHERE chat_id=?', (None, chat_id))
        conn.commit()
        conn.close()
    #Список всех каналов приемников
    def get_channels(self, chat_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT channel_id, title FROM channels WHERE chat_id = ?', (chat_id,))
        data = cursor.fetchall()
        conn.close()
        if data:
            channels = []
            for channel in data:
                channels.append((channel[0],channel[1]))
            return channels
        else:
            return False
    #Каналы доноры
    def get_donors(self, channel_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT donor_id, donor_title FROM donors WHERE channel_id = ?', (channel_id,))
        data = cursor.fetchall()
        conn.close()
        donors = []
        for d in data:
            donors.append((d[0], d[1]))
        return donors
    #Информация о канале
    def get_channel_info(self, channel_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT title, username FROM channels WHERE channel_id = ?', (channel_id,))
        data = cursor.fetchone()
        conn.close()
        return data
    #Информация о доноре

    def get_donor_info(self, channel_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT channel_id, donor_title, donor_username FROM donors WHERE donor_id = ?', (channel_id,))
        data = cursor.fetchone()
        conn.close()
        return data
    #Удаление донора
    def delete_donor(self, donor_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM donors WHERE donor_id=?', (donor_id,))
        conn.commit()
        conn.close()
    #Удаление канала
    def delete_channnel(self, channel_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM channels WHERE channel_id=?', (channel_id,))
        cursor.execute('DELETE FROM donors WHERE channel_id=?', (channel_id,))
        conn.commit()
        conn.close()
    ###### Просмотры ########
    #Записываем дипазон накрутки просмотров в базу
    def update_prosmotri_diapazon(self, chat_id, diapazon):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT channel_id FROM channels WHERE status = ? AND chat_id = ?', ('prosmotri', chat_id))
        channel_id = cursor.fetchone()[0]
        cursor.execute(f'UPDATE channels SET prosmotri_diapazon = ? WHERE channel_id=?', (diapazon, channel_id))
        cursor.execute(f'UPDATE channels SET status = ? WHERE channel_id=?', (None, channel_id))

        conn.commit()
        conn.close()
        return channel_id
    #Возвращает диапазон просмотров
    def get_prosmotri_diapazon(self, channel_id, chat_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT prosmotri_diapazon FROM channels WHERE channel_id = ? AND chat_id = ?', (channel_id,chat_id))
        data = cursor.fetchone()
        conn.close()
        return data
    #######################
    ########## Лимиты доноров #########
    def get_donors_limits(self, donor_id, channel_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT limit_count, limit_period FROM donors WHERE channel_id = ? AND donor_id = ?', (channel_id, donor_id))
        data = cursor.fetchone()
        conn.close()
        return data
    def update_donors_limits(self, donor_id, channel_id, option, info):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        if  option in ['CountDec', 'CountInc']:
            if option == 'CountDec':
                if not info[0]:
                    limit_count = None
                    limit_period = None
                elif info[0] == 1:
                    limit_count = None
                    limit_period = None
                else:
                    limit_count = info[0]-1
                    limit_period = info[1]
            elif option == 'CountInc':
                if not info[0]:
                    limit_count = 1
                    limit_period = 'Час'
                else:
                    limit_count = info[0]+1
                    limit_period = info[1]
        elif option == 'Period':
            if not info[1]:
                limit_count = 1
                limit_period = 'Час'
            elif info[1] == 'Час':
                limit_count = info[0]
                limit_period = 'День'
            elif info[1] == 'День':
                limit_count = info[0]
                limit_period = 'Час'
        elif option == 'Del':
            limit_count = None
            limit_period = None
        cursor.execute(f'UPDATE donors SET limit_count = ? WHERE channel_id = ? AND donor_id = ?', (limit_count, channel_id, donor_id))
        cursor.execute(f'UPDATE donors SET limit_period = ? WHERE channel_id = ? AND donor_id = ?', (limit_period, channel_id, donor_id))
        conn.commit()
        conn.close()
        return (limit_count, limit_period)
    #######################
    # Функция для получения медиагруппы из базы данных
    def get_media_group_from_db(self, grouped_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT media_type, file_id FROM media_group WHERE grouped_id = ?', (grouped_id,))
        media_group = cursor.fetchall()
        media_files = []
        n = 0
        for media_type, file_id in media_group:
            n+=1
            if media_type == 'photo':
                media_files.append(types.InputMediaPhoto(file_id))
            elif media_type == 'video':
                media_files.append(types.InputMediaVideo(file_id))
        conn.close()
        return media_files, n
    def delete_media_group(self, grouped_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('SELECT media_type FROM media_group WHERE grouped_id = ?', (grouped_id,))
        media_group = cursor.fetchall()
        cursor.execute('DELETE FROM media_group WHERE grouped_id = ?', (grouped_id,))
        conn.commit()
        conn.close()
        return len(media_group)
