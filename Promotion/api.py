import random
import requests


class StreamPromotionAPI:
    def __init__(self):
        self.api_key = '5u6W5lQDw2OVCyKFwCtB3MDAbjRTQbx6'
        self.api_url = "https://stream-promotion.ru/api/v2"
        self.service_id = "27126"

    def create_order(self, link: str, diapazon):
        headers = {
            'User-Agent': 'MyApp/1.0'
        }
        diap = diapazon[0].split(' ')
        diapazon = random.randint(int(diap[0]), int(diap[1]))
        if diapazon >=100:
            service_id = '27126'
        elif diapazon<100:
            service_id = '27356'
        payload = {
            "key": self.api_key,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": diapazon
        }
        response = requests.post(self.api_url, json=payload, headers=headers)
        return response
