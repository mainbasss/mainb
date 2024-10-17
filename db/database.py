import sqlite3
import os
from datetime import datetime, timedelta
from telebot import types

class Database:
    def __init__(self, db_name='base.db'):
        self.folder_name = 'files'
        os.makedirs(self.folder_name, exist_ok=True)
        self.db_file = os.path.join(self.folder_name, db_name)
        self.create_tables()


    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS channels (
                chat_id INTEGER NOT NULL,
                channel_id INTEGER,
                title TEXT,
                username TEXT,
                status TEXT,
                prosmotri_diapazon TEXT)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS donors (
                channel_id INTEGER,
                donor_id INTEGER,
                donor_title TEXT,
                donor_username TEXT,
                limit_count INTEGER,
                limit_period TEXT,
                start_period TEXT,
                send_message_count INTEGER)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS media_group (
                grouped_id TEXT,
                message_id INTEGER,
                chat_id INTEGER,
                media_type TEXT,
                file_id TEXT)''')

    def connect(self):
        return sqlite3.connect(self.db_file)

class Channel:
    def __init__(self, db: Database):
        self.db = db

    def add(self, chat_id, channel_id, title, username):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM channels WHERE channel_id = ?', (channel_id,))
            if cursor.fetchone() is None:
                cursor.execute('INSERT INTO channels (chat_id, channel_id, title, username) VALUES (?, ?, ?, ?)',
                               (chat_id, channel_id, title, username))
                return True
            return False

    def delete(self, channel_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM channels WHERE channel_id = ?', (channel_id,))
            cursor.execute('DELETE FROM donors WHERE channel_id = ?', (channel_id,))

    def get_channels(self, chat_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT channel_id, title FROM channels WHERE chat_id = ?', (chat_id,))
            data = cursor.fetchall()
            if data:
                channels = []
                for channel in data:
                    channels.append((channel[0],channel[1]))
                return channels
            else:
                return False

    def update_prosmotri_diapazon(self, chat_id, diapazon):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT channel_id FROM channels WHERE status = ? AND chat_id = ?', ('prosmotri', chat_id))
            channel_id = cursor.fetchone()[0]
            cursor.execute('UPDATE channels SET prosmotri_diapazon = ? WHERE channel_id=?', (diapazon, channel_id))
            cursor.execute('UPDATE channels SET status = ? WHERE channel_id=?', (None, channel_id))

            return channel_id

    def get_prosmotri_diapazon(self, channel_id, chat_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT prosmotri_diapazon FROM channels WHERE channel_id = ? AND chat_id = ?', (channel_id, chat_id))
            data = cursor.fetchone()
            return data

    def get_info(self, channel_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT title, username FROM channels WHERE channel_id = ?', (channel_id,))
            return cursor.fetchone()

    def get_chat_id(self, donor):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT channel_id FROM donors WHERE donor_id = ?', (donor,))
            channels = cursor.fetchall()
            chat_ids = []
            for ch in channels:
                cursor.execute('SELECT chat_id FROM channels WHERE channel_id = ?', (ch[0],))
                data = cursor.fetchone()
                if data and data[0] not in chat_ids:
                    chat_ids.append(data[0])
            return chat_ids

    def get_name(self, channel_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT donor_title FROM donors WHERE donor_id = ?', (channel_id,))
            donor_name = cursor.fetchone()[0]

            cursor.execute('SELECT username FROM channels WHERE channel_id IN (SELECT channel_id FROM donors WHERE donor_id = ?)', (channel_id,))
            usernames = [data[0] for data in cursor.fetchall()]
            return donor_name, usernames
    def update_status(self, channel_id, status):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE channels SET status = ? WHERE channel_id=?', (status, channel_id))
            conn.commit()

    def del_status(self, chat_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'UPDATE channels SET status = ? WHERE chat_id=?', (None, chat_id))
            conn.commit()


class Donor:
    def __init__(self, db: Database):
        self.db = db

    def add(self, chat_id, donor_id, donor_title, donor_username):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT channel_id FROM channels WHERE status = ? AND chat_id = ?', ('wait',chat_id))
            channel_id = cursor.fetchone()[0]
            cursor.execute('SELECT * FROM donors WHERE donor_id = ?', (donor_id,))
            if cursor.fetchone() is None:
                cursor.execute('INSERT INTO donors (channel_id, donor_id, donor_title, donor_username) VALUES (?, ?, ?, ?)',
                               (channel_id, donor_id, donor_title, donor_username))
                return channel_id
            return False

    def delete(self, donor_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM donors WHERE donor_id = ?', (donor_id,))

    def get_limits(self, donor_id, channel_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT limit_count, limit_period FROM donors WHERE channel_id = ? AND donor_id = ?', (channel_id, donor_id))
            return cursor.fetchone()

    def update_limits(self, donor_id, channel_id, option, info):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            if option in ['CountDec', 'CountInc']:
                if option == 'CountDec':
                    if not info[0]:
                        limit_count = None
                        limit_period = None
                    elif info[0] == 1:
                        limit_count = None
                        limit_period = None
                    else:
                        limit_count = info[0] - 1
                        limit_period = info[1]
                elif option == 'CountInc':
                    if not info[0]:
                        limit_count = 1
                        limit_period = 'Час'
                    else:
                        limit_count = info[0] + 1
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

            cursor.execute('UPDATE donors SET limit_count = ? WHERE channel_id = ? AND donor_id = ?', (limit_count, channel_id, donor_id))
            cursor.execute('UPDATE donors SET limit_period = ? WHERE channel_id = ? AND donor_id = ?', (limit_period, channel_id, donor_id))

            return (limit_count, limit_period)

    def get_info(self, donor_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT channel_id, donor_title, donor_username FROM donors WHERE donor_id = ?', (donor_id,))
            return cursor.fetchone()

    def get_donors_for_parser(self):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT donor_id FROM donors')
            data = cursor.fetchall()
            return tuple(d[0] for d in data)

    def get_donors(self, channel_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute(f'SELECT donor_id, donor_title FROM donors WHERE channel_id = ?', (channel_id,))
            data = cursor.fetchall()
            donors = []
            for d in data:
                donors.append((d[0], d[1]))
            return donors

    def get_donor_username(self, channel_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT donor_username FROM donors WHERE donor_id = ?', (channel_id,))
            data = cursor.fetchone()
            return data[0]

    def get_limit(self, chat_id, donor_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT channel_id FROM donors WHERE donor_id = ?', (donor_id,))
            data = cursor.fetchall()
            for ch in data:
                cursor.execute('SELECT channel_id FROM channels WHERE channel_id = ? AND chat_id = ?', (ch[0], chat_id))
                data = cursor.fetchone()
                if data:
                    channel_id = ch[0]
                    break

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

            if not start_period:
                send_message_count = 0
                start_period = now.isoformat()
            start_period_time = datetime.fromisoformat(start_period)

            if limit_period == 'Час':
                period_duration = timedelta(hours=1)
            elif limit_period == 'День':
                period_duration = timedelta(days=1)
            else:
                raise ValueError("Неподдерживаемый период: {}".format(limit_period))

            if now - start_period_time >= period_duration:
                send_message_count = 0
                start_period = now.isoformat()
            else:
                if send_message_count >= limit_count:
                    return False

            send_message_count += 1
            cursor.execute("""
                UPDATE donors
                SET start_period = ?, send_message_count = ?
                WHERE channel_id = ? AND donor_id = ?
            """, (start_period, send_message_count, channel_id, donor_id))

            conn.commit()
            return True

class MediaGroup:
    def __init__(self, db: Database):
        self.db = db

    def add(self, grouped_id, message_id, chat_id, media_type, file_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO media_group (grouped_id, message_id, chat_id, media_type, file_id) VALUES (?, ?, ?, ?, ?)',
                           (grouped_id, message_id, chat_id, media_type, file_id))

    def get(self, grouped_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT media_type, file_id FROM media_group WHERE grouped_id = ?', (grouped_id,))
            return cursor.fetchall()

    def delete(self, grouped_id):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM media_group WHERE grouped_id = ?', (grouped_id,))

    def save_media_group(self, grouped_id, chat_id, message_id, media_files):
        with self.db.connect() as conn:
            cursor = conn.cursor()
            for media in media_files:
                media_type = 'photo' if isinstance(media, types.InputMediaPhoto) else 'video'
                file_id = media.media
                cursor.execute('INSERT INTO media_group (grouped_id, message_id, chat_id, media_type, file_id) VALUES (?, ?, ?, ?, ?)',
                               (grouped_id, message_id, chat_id, media_type, file_id))
            conn.commit()
