# main.py
from Promotion import promotion_manger

# Тестовый вызов
async def test_api():
    link = "https://t.me/test_channel/test_message"
    diapazon = (50, 100)  # Пример диапазона от 50 до 100
    response = promotion_manger.distribute_views(link, diapazon)
    print(response)

# Запуск теста
if __name__ == "__main__":
    import asyncio
    asyncio.run(test_api())
