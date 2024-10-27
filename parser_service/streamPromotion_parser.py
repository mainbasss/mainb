import requests
from Promotion import STREAM_PROMOTION_API_KEY
from db.promotion_database import streamPromotion
streamPromotionDB = streamPromotion()
def get_orders():
    api_key = STREAM_PROMOTION_API_KEY
    api_url = "https://stream-promotion.ru/api/v2"
    headers = {
        'User-Agent': 'MyApp/1.0'
    }
    payload = {
        "key": api_key,
        "action": "services",
    }
    response = requests.post(api_url, json=payload, headers=headers)
    orders = response.json()
    return orders

all_orders = get_orders()
orders = []
for order in all_orders:
    if 'TG Просмотры' in order['name']:
        orders.append(order)

sorted_orders = sorted(orders, key=lambda x: x['rate'])
streamPromotionDB.save_parsed_orders(sorted_orders)
print(sorted_orders[0])
print(sorted_orders[0].keys())
