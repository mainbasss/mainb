import os

from telethon import TelegramClient, errors
from telethon.sessions import StringSession #Временно
from telethon.tl.functions.channels import JoinChannelRequest
from telethon import events
from dotenv import load_dotenv

import telebot
from telebot import types
from .format import format_message
import asyncio
import traceback
from parser_service.gpt import long_message
from parser_service import *
# Название файла сессии и данные API

load_dotenv()
bot = telebot.TeleBot(TOKEN)
# Подключение через файл сессии
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)



async def check_new_channels():
    dialogs = await client.get_dialogs()

    # Фильтруем только каналы
    channels = [dialog for dialog in dialogs if dialog.is_channel]

    ids = []
    for channel in channels:
        ids.append(channel.id)
    #print('ids',ids)
    current_channels = donor_instance.get_donors_for_parser()  # Получаем актуальный список каналов из базы
    #print('current_channels',current_channels)
    for channel in current_channels:
        if channel not in ids:
            print(channel)
            print(donor_instance.get_donor_username(channel))
            username = 'https://t.me/'+donor_instance.get_donor_username(channel)
            try:
                # Пробуем присоединиться к новому каналу
                await client(JoinChannelRequest(username))
                print(f"Подписался на канал: {username}")
            except Exception as e:
                print(f"Не удалось подписаться на канал {username}: {e}")

async def refresh_channels():
    while True:
        await check_new_channels()
        await asyncio.sleep(30)  # Проверяем каждые 5 минут

async def main():
    try:
        # Попытка стартовать клиента с существующей сессией
        await client.start()

        # Проверяем, успешно ли выполнено подключение
        me = await client.get_me()
        if me:
            print(f"Сессия актуальна! Подключен как: {me.first_name}")
            # Запускаем мониторинг новых каналов в фоновом режиме
            client.loop.create_task(refresh_channels())
            #########################
            @client.on(events.NewMessage)
            async def handler_new_message(event):
                donors = donor_instance.get_donors_for_parser()
                try:
                    ch = event.message.peer_id.channel_id
                    flag = True
                except:
                    flag = False
                if flag:
                    if int(f'-100{event.message.peer_id.channel_id}') in [int(donor) for donor in donors]:
                        try:
                            donor_id = int(f'-100{event.message.peer_id.channel_id}')
                            if event.message.entities:
                                message_text = format_message(event.message)#event.message.message
                            else:
                                message_text = event.message.message
                            inline_markup = types.InlineKeyboardMarkup(row_width=2)
                            inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"first_confirm_{donor_id}"),
                                    types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"first_refuse_{donor_id}"))
                            inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"first_edit_{donor_id}"))
                            donor_name, channelels = channel_instance.get_name(donor_id)
                            str_channelels = ', @'.join(channelels)

                            if event.message.photo or event.message.video:
                                count = 774
                            else:
                                count = 3840
                            while True:
                                if len(message_text)>count:
                                    message_text = long_message(message_text, count)
                                    print(len(message_text))
                                else:
                                    break
                            message_text = (
                                    f'<b>🥳 Вышел новый пост в каналe: </><code>{donor_name}</>\n\n'
                                    f'{message_text}\n\n'
                                    f'<b>К данному источнику(<code>{donor_name}</>) привязанные данный(ые) канал(ы): @{str_channelels}</>'
                                    )
                            chat_ids = channel_instance.get_chat_id(donor_id)
                            # Проверяем, если сообщение является частью медиа-группы (альбома)
                            if event.message.grouped_id:
                                grouped_id = event.message.grouped_id

                                # Получаем все сообщения, относящиеся к этому grouped_id
                                media_messages = await client.get_messages(event.chat_id, min_id=event.message.id - 10, max_id=event.message.id + 10)

                                # Фильтруем и сортируем сообщения, чтобы собрать только те, что принадлежат медиа-группе, и расположить их в правильном порядке
                                media_messages = sorted([msg for msg in media_messages if msg.grouped_id == grouped_id], key=lambda m: m.id)
                                media_files = []

                                # Проверяем, если сообщение является частью медиа-группы (альбома)
                                if event.message.grouped_id:
                                    grouped_id = event.message.grouped_id

                                    # Получаем все сообщения, относящиеся к этому grouped_id
                                    media_messages = await client.get_messages(event.chat_id, min_id=event.message.id - 10, max_id=event.message.id + 10)

                                    # Фильтруем и сортируем сообщения, чтобы собрать только те, что принадлежат медиа-группе, и расположить их в правильном порядке
                                    media_messages = sorted([msg for msg in media_messages if msg.grouped_id == grouped_id], key=lambda m: m.id)
                                    media_files = []

                                    # Если это первое сообщение из группы (по id), отправляем медиа-группу
                                    if media_messages[0].id == event.message.id:
                                        for media_message in media_messages:
                                            caption = media_message.message  # Получаем подпись медиа
                                            if caption!='':
                                                if media_message.entities:
                                                    message_text = format_message(media_message)
                                                else:
                                                    message_text = caption

                                            # Если это фото
                                            if media_message.photo:
                                                file = await client.download_file(media_message.photo)
                                                media_files.append(types.InputMediaPhoto(file))

                                            # Если это видео
                                            elif media_message.video:
                                                file = await client.download_file(media_message.video)
                                                media_files.append(types.InputMediaVideo(file))

                                        # Отправляем медиа-группу без разметки
                                        if media_files:
                                            media_group_instance.save_media_group(grouped_id, event.chat_id, event.message.id, media_files)
                                            for chat_id in chat_ids:
                                                bot.send_media_group(chat_id=chat_id, media=media_files)

                                        # Проверяем, что message_text не пуст перед отправкой
                                        if message_text.strip():  # Если message_text не пустой
                                            inline_markup = types.InlineKeyboardMarkup(row_width=2)
                                            inline_markup.add(types.InlineKeyboardButton(text = '✅Принять', callback_data=f"first_confirm_{donor_id}_media{grouped_id}"),
                                                    types.InlineKeyboardButton(text = '❌Отклонить', callback_data=f"first_refuse_{donor_id}_media{grouped_id}"))
                                            inline_markup.add(types.InlineKeyboardButton(text = '✏️Редактировать', callback_data=f"first_edit_{donor_id}_media{grouped_id}"))
                                            while True:
                                                if len(message_text)>774:
                                                    message_text = long_message(message_text, 774)
                                                else:
                                                    break
                                            message_text = (
                                                    f'<b>🥳 Вышел новый пост в каналe: </><code>{donor_name}</>\n\n'
                                                    f'{message_text}\n\n'
                                                    f'<b>К данному источнику(<code>{donor_name}</>) привязанные данный(ые) канал(ы): @{str_channelels}</>'
                                                    )
                                            for chat_id in chat_ids:

                                                bot.send_message(chat_id=chat_id,
                                                                 text=message_text,
                                                                 reply_markup=inline_markup,
                                                                 parse_mode='HTML')
                            # Проверка на фото
                            elif event.message.photo:
                                largest_photo = event.message.photo
                                file = await client.download_file(largest_photo)
                                for chat_id in chat_ids:
                                    if donor_instance.get_limit(chat_id, donor_id):
                                        bot.send_photo(chat_id=chat_id,
                                                       photo=file,
                                                       caption=message_text,
                                                       reply_markup=inline_markup,
                                                       parse_mode='HTML')

                            # Проверка на видео
                            elif event.message.video:
                                video = event.message.video
                                file = await client.download_file(video)
                                for chat_id in chat_ids:
                                    if donor_instance.get_limit(chat_id, donor_id):
                                        bot.send_video(chat_id=chat_id,
                                                       video=file,
                                                       caption=message_text,
                                                       reply_markup=inline_markup,
                                                       parse_mode='HTML')
                            else:
                                # Если нет медиа, отправляем обычное текстовое сообщение
                                for chat_id in chat_ids:
                                    if donor_instance.get_limit(chat_id, donor_id):
                                        bot.send_message(chat_id,
                                                         message_text,
                                                         reply_markup=inline_markup,
                                                         parse_mode='HTML')



                        except Exception as e:
                            print(traceback.format_exc())

            await client.run_until_disconnected()
        else:
            print("Не удалось получить информацию о пользователе.")

    except errors.SessionPasswordNeededError:
        print("Сессия требует пароль двухфакторной аутентификации.")

    except errors.PhoneCodeInvalidError:
        print("Неверный код подтверждения.")

    except Exception as e:
        print(f"Сессия не актуальна или произошла ошибка: {e}")
if __name__ == '__main__':
    client.loop.run_until_complete(main())
