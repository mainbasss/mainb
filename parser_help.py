import json
import os
from telebot import types
import sqlite3
from datetime import datetime, timedelta
from time import sleep

##########
#Data base
class Base():
    def __init__(self):
        folder_name = 'files'
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        self.db_file = os.path.join(folder_name, 'base.db')

    def get_donors(self):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT donor_id FROM donors')
        data = cursor.fetchall()
        conn.close()
        donors = ()
        for d in data:
            if d[0] not in donors:
                donors+=(d[0],)
        return donors

    def get_chat_id(self, donor):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT channel_id FROM donors WHERE donor_id = ?', (donor,))
        data = cursor.fetchall()
        channels = []
        for ch in data:
            channels.append(ch[0])
        chat_ids = []
        for ch in channels:
            cursor.execute(f'SELECT chat_id FROM channels WHERE channel_id = ?', (ch,))
            data = cursor.fetchone()
            if data[0] not in chat_ids:
                chat_ids.append(data[0])
        conn.close()
        return chat_ids
    def get_name(self, channel_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT donor_title, channel_id FROM donors WHERE donor_id = ?', (channel_id,))
        data = cursor.fetchall()
        donor_name = data[0][0]
        ch_ids = []
        for ch in data:
            ch_ids.append(ch[1])
        usernames = []
        for ch in ch_ids:
            cursor.execute(f'SELECT username FROM channels WHERE channel_id = ?', (ch,))
            data = cursor.fetchone()
            usernames.append(data[0])
        conn.close()
        return donor_name, usernames
    def get_donor_username(self, channel_id):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT donor_username FROM donors WHERE donor_id = ?', (channel_id,))
        data = cursor.fetchone()
        conn.close()
        return data[0]
    #Возвращает достигнут лимит или нет
    def get_limit(self, chat_id, donor_id):
        # Подключаемся к базе данных
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute(f'SELECT channel_id FROM donors WHERE donor_id = ?', (donor_id,))
        data = cursor.fetchall()
        for ch in data:
            cursor.execute(f'SELECT channel_id FROM channels WHERE channel_id = ? AND chat_id = ?', (ch[0], chat_id))
            data = cursor.fetchone()
            if data:
                channel_id = ch[0]
                break
        # Получаем информацию о доноре
        cursor.execute("""
            SELECT limit_count, limit_period, start_period, send_message_count
            FROM donors
            WHERE channel_id = ? AND donor_id = ?
        """, (channel_id, donor_id))

        row = cursor.fetchone()

        now = datetime.now()

        limit_count, limit_period, start_period, send_message_count = row
        if not limit_count:
            return True
        # Преобразуем start_period в datetime
        if not start_period:
            send_message_count = 0
            start_period = now.isoformat()
        start_period_time = datetime.fromisoformat(start_period)

        # Определяем период

        if limit_period == 'Час':
            period_duration = timedelta(hours=1)
        elif limit_period == 'День':
            period_duration = timedelta(days=1)
        else:
            raise ValueError("Неподдерживаемый период: {}".format(limit_period))

        # Проверяем, истек ли период
        if now - start_period_time >= period_duration:
            # Период истек, сбрасываем счётчик и обновляем `start_period`
            send_message_count = 0
            start_period = now.isoformat()
        else:
            # Период еще не истек
            if send_message_count >= limit_count:
                # Лимит превышен
                conn.close()
                return False

        # Увеличиваем счётчик отправленных сообщений
        send_message_count += 1

        # Обновляем данные в базе
        cursor.execute("""
            UPDATE donors
            SET start_period = ?, send_message_count = ?
            WHERE channel_id = ? AND donor_id = ?
        """, (start_period, send_message_count, channel_id, donor_id))

        conn.commit()
        conn.close()
        return True  # Сообщение может быть отправлено
    #Запись медиагруппы
    def save_media_group(self, grouped_id, chat_id, message_id, media_files):
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        for media in media_files:
            media_type = 'photo' if isinstance(media, types.InputMediaPhoto) else 'video'
            file_id = media.media  # file_id для фото или видео
            cursor.execute('INSERT INTO media_group (grouped_id, message_id, chat_id, media_type, file_id) VALUES (?, ?, ?, ?, ?)',
                           (grouped_id, message_id, chat_id, media_type, file_id))
        conn.commit()
