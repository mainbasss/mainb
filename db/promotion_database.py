import os
import sqlite3

class Justanotherpanel:
    def __init__(self, db_name='base.db'):
        self.folder_name = 'files'
        os.makedirs(self.folder_name, exist_ok=True)
        self.db_file = os.path.join(self.folder_name, db_name)
        self.create_tables()

    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            # justanotherpanel
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS justanotherpanel (
                    service_id TEXT PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    rate REAL,
                    min_order INTEGER,
                    max_order INTEGER,
                    dripfeed INTEGER,
                    refill INTEGER,
                    cancel INTEGER,
                    category TEXT
                )
            ''')
    def connect(self):
        return sqlite3.connect(self.db_file)

    def save_parsed_orders(self, orders):
        with self.connect() as conn:
            cursor = conn.cursor()

            # Список всех существующих service_id в базе данных
            existing_service_ids = {row[0] for row in cursor.execute('SELECT service_id FROM justanotherpanel')}

            # Список service_id из новых заказов
            new_service_ids = {order['service'] for order in orders}

            # Обновляем или добавляем новые предложения
            for order in orders:
                cursor.execute('''
                    INSERT INTO justanotherpanel (service_id, name, type, rate, min_order, max_order, dripfeed, refill, cancel, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(service_id) DO UPDATE SET
                        name = excluded.name,
                        rate = excluded.rate,
                        min_order = excluded.min_order,
                        max_order = excluded.max_order,
                        dripfeed = excluded.dripfeed,
                        refill = excluded.refill,
                        cancel = excluded.cancel,
                        category = excluded.category
                ''', (
                    order['service'],
                    order['name'],
                    order['type'],
                    float(order['rate']),
                    int(order['min']),
                    int(order['max']),
                    order['dripfeed'],
                    order['refill'],
                    order['cancel'],
                    order['category']
                ))

            # Удаляем устаревшие предложения
            obsolete_service_ids = existing_service_ids - new_service_ids
            if obsolete_service_ids:
                cursor.execute('''
                    DELETE FROM justanotherpanel WHERE service_id IN ({})
                '''.format(','.join('?' * len(obsolete_service_ids))), list(obsolete_service_ids))

            conn.commit()

class streamPromotion:
    def __init__(self, db_name='base.db'):
        self.folder_name = 'files'
        os.makedirs(self.folder_name, exist_ok=True)
        self.db_file = os.path.join(self.folder_name, db_name)
        self.create_tables()

    def create_tables(self):
        with self.connect() as conn:
            cursor = conn.cursor()
            # streamPromotion
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS streamPromotion (
                    service_id TEXT PRIMARY KEY,
                    name TEXT,
                    type TEXT,
                    rate REAL,
                    min INTEGER,
                    max INTEGER,
                    dripfeed INTEGER,
                    refill INTEGER,
                    desc INTEGER,
                    category TEXT,
                    multiple INTEGER
                )
            ''')
    def connect(self):
        return sqlite3.connect(self.db_file)

    def save_parsed_orders(self, orders):
        with self.connect() as conn:
            cursor = conn.cursor()

            # Список всех существующих service_id в базе данных
            existing_service_ids = {row[0] for row in cursor.execute('SELECT service_id FROM streamPromotion')}

            # Список service_id из новых заказов
            new_service_ids = {order['service'] for order in orders}

            # Обновляем или добавляем новые предложения
            for order in orders:
                cursor.execute('''
                    INSERT INTO streamPromotion (service_id, name, type, rate, min, max, dripfeed, refill, desc, category, multiple)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(service_id) DO UPDATE SET
                        name = excluded.name,
                        rate = excluded.rate,
                        min = excluded.min,
                        max = excluded.max,
                        dripfeed = excluded.dripfeed,
                        refill = excluded.refill,
                        desc = excluded.desc,
                        category = excluded.category,
                        multiple = excluded.multiple

                ''', (
                    order['service'],
                    order['name'],
                    order['type'],
                    float(order['rate']),
                    int(order['min']),
                    int(order['max']),
                    order['dripfeed'],
                    order['refill'],
                    order['desc'],
                    order['category'],
                    order['multiple']
                ))

            # Удаляем устаревшие предложения
            obsolete_service_ids = existing_service_ids - new_service_ids
            if obsolete_service_ids:
                cursor.execute('''
                    DELETE FROM streamPromotion WHERE service_id IN ({})
                '''.format(','.join('?' * len(obsolete_service_ids))), list(obsolete_service_ids))

            conn.commit()
