import random
import requests
import os
from Promotion import STREAM_PROMOTION_API_KEY
class StreamPromotionAPI:
    BASE_URL = "https://stream-promotion.ru/api/v2"
    API_KEY = STREAM_PROMOTION_API_KEY
    headers = {
        'User-Agent': 'MyApp/1.0'
    }

    def __init__(self):

        if not STREAM_PROMOTION_API_KEY:
            raise ValueError("API Key not set!")


    def create_order(self, link: str, value: int):
        print('StreamPromotionAPI value', value)
        if value<10:
            value = 10
        if value >= 100:
            service_id = '27126'
        elif value < 100:
            service_id = '28730'
        print('StreamPromotionAPI service_id', service_id)
        payload = {
            "key": self.API_KEY,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": value
        }

        response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
        print(response.json())
        if response.status_code == 200:
            return response.json()  # Возврат JSON ответа
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None  # Обработка ошибок


    def check_order_status(self, order_id):
        payload = {
                "key": self.API_KEY,
                "action": "status",
                "ORDER": order_id,
                }

        response = requests.post(self.BASE_URL, json=payload, headers=self.headers)
        print(response.json())
        if response.status_code == 200:
            return response.json()  # Возврат JSON ответа
        else:
            print(f"Error: {response.status_code}, {response.text}")
            return None  # Обработка ошибок
