import requests
from Promotion import justanother_api
from db.promotion_database import Justanotherpanel
justanotherpanelDB = Justanotherpanel()
def get_orders():
    BASE_URL = "https://justanotherpanel.com/api/v2"
    API_KEY = justanother_api
    headers = {
        'User-Agent': 'MyApp/1.0'
    }
    payload = {
        "key": API_KEY,
        "action": "services",
    }

    response = requests.post(BASE_URL, data=payload, headers = headers )
    return response.json()

all_orders = get_orders()
orders = []
for order in all_orders:
    if 'Telegram Views' in order['name'] or 'Telegram Post Views' in order['name'] or 'Telegram Auto Views' in order['name']:

        orders.append(order)

sorted_orders = sorted(orders, key=lambda x: x['rate'])
justanotherpanelDB.save_parsed_orders(sorted_orders)
print(sorted_orders[0])
print('######## TG',len(orders))
print('######## ALL',len(all_orders))
