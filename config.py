from os import environ
from dotenv import load_dotenv

# Загрузка значений переменных окружения
load_dotenv()

API_ID = environ.get('API_ID')
API_HASH = environ.get('API_HASH')
SESSION_STRING = environ.get('SESSION_STRING')
TOKEN = environ.get('TOKEN')
session_file = environ.get('session_file')
api_id = environ.get('api_id')
api_hash = environ.get('api_hash')
