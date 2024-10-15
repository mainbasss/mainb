

# Определяем классы для различных форматировок текста
class Message:
    def __init__(self, id, peer_id, date, message, entities):
        self.id = id
        self.peer_id = peer_id
        self.date = date
        self.message = message
        self.entities = entities


class MessageEntityBold:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length


class MessageEntityItalic:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length


class MessageEntityCode:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length


class MessageEntityPre:
    def __init__(self, offset, length, language):
        self.offset = offset
        self.length = length
        self.language = language


class MessageEntitySpoiler:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length


class MessageEntityStrike:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length


class MessageEntityTextUrl:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length

class MessageEntityHashtag:
    def __init__(self, offset, length):
        self.offset = offset
        self.length = length


def format_message(message):
    formatted_parts = []
    text = message.message
    last_index = 0
    for entity, txt in message.get_entities_text():
        if entity.__class__.__name__ == "MessageEntityBold":
            text = text.replace(txt, f'<b>{txt}</b>')
        elif entity.__class__.__name__ == "MessageEntityItalic":
            text = text.replace(txt, f'<i>{txt}</i>')
        elif entity.__class__.__name__ == "MessageEntityCode":
            text = text.replace(txt, f'<code>{txt}</code>')
        elif entity.__class__.__name__ == "MessageEntityPre":
            text = text.replace(txt, f'<pre>{txt}</pre>')
        elif entity.__class__.__name__ == "MessageEntitySpoiler":
            text = text.replace(txt, f'<span class="tg-spoiler">{txt}</span>')
        elif entity.__class__.__name__ == "MessageEntityStrike":
            text = text.replace(txt, f'<s>{txt}</s>')
        elif entity.__class__.__name__ == "MessageEntityTextUrl":
            text = text.replace(txt, f'<a href="{entity.url}">{txt}</a>')

    return text
