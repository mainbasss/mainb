from openai import OpenAI
from parser_service import api_key
client = OpenAI(api_key=api_key)


prompts = (
    'Ты профессиональный бизнес копирайтер, твоя задача переписывать и уникализировать текста которые я тебе пришлю!'
    'Твои главные фильтры:'
    '1. преобразовывай все ссылки из Markdown вида [Текст ссылки](https://www.site.ru/) в формат HTML вида <a href="http://site.ru">текст ссылки</a>'
    'если имеются ссылки начинающиеся с символа @, их не нужно указывать, удаляй из текста.'
    '2. Ты должен использовать красивые абзацы как в aiogram python'
    '3. Ты должен использовать теги такие как <b></b> или <i></i> вместо **, это обязательно!, для отметки интересных моментов. Используй только теги <b>, <i>, <code>, <pre>, <span class="tg-spoiler">, <s>, <a href="url"> другие теги использовать ЗАПРЕЩЕНО. Не используй <li>, <h2>, <p>, <ul>'
    '4. Ты должен добавлять эмоджи по смыслу, но чаще всего в заголовке'
    '5. Ты должен убирать из постов названия чужих каналов, они обычно помечены в ***'
    '6. ТЫ НЕ ДОЛЖЕН ДОПУСТИТЬ НЕ ЕДИНОЙ ССЫЛКИ В ОТВЕТЕ, НЕ ЕДИНОЙ РЕКЛАМЫ'
)


def gpt_message(prompt):
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": prompts},
        {"role": "user", "content": prompt},
      ]
    )
    return response.choices[0].message.content

def long_message(prompt, count):
    prompts = f'Сократи текст до {count} символов, что бы не потерять смысл'
    response = client.chat.completions.create(
      model="gpt-4o-mini",
      messages=[
        {"role": "system", "content": prompts},
        {"role": "user", "content": prompt},
      ]
    )
    return response.choices[0].message.content
