from config import TOKEN
from db.database import Database
from db.database import Channel
from db.database import Donor
from db.database import MediaGroup
from bot_service.mark import Mark
from bot_service.files import Files 

# Создание экземпляров классов
database_instance = Database()
channel_instance = Channel(database_instance)
donor_instance = Donor(database_instance)
media_group_instance = MediaGroup(database_instance)
mark = Mark()
files = Files()

__all__ = ['database_instance', 'channel_instance', 'donor_instance', 'media_group_instance', 'mark', 'files', 'TOKEN']
