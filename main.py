import asyncio
import os

from telethon import TelegramClient, events, sync
from aiogram import Bot, Dispatcher, executor
from telethon.tl.functions.messages import GetHistoryRequest

from config import BOT_TOKEN, api_id, api_hash, phone, channel_names, accepted_users, DELAY
from telethon.errors import SessionPasswordNeededError


# создаем необходимые папки
if not os.path.exists('session'):
    os.makedirs('session')

if not os.path.exists('video'):
    os.makedirs('video')

if not os.path.exists('db'):
    os.makedirs('db')

# создаем экземпляр бота aiogram
loop = asyncio.get_event_loop()
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot, loop=loop)

# создаем экземпляр клиента телеграм telethon
client = TelegramClient('session/' + phone, api_id, api_hash)
client.connect()


async def read_all_messages(channel_name):
    messages = []
    message_history = await client(
        GetHistoryRequest(peer=channel_name, limit=1000, offset_date=None, offset_id=0, max_id=0, min_id=0, add_offset=0,
                          hash=0))
    if not message_history.messages:
        return
    for message in message_history.messages:
        if message.message:
            messages.append({'message_id': message.id,
                             'message_text': message.message,
                             'media_id': message.media.document.id})

    return messages


async def schedule(myself, wait_time):
    while True:
        await client.send_message(accepted_users[0], f'Запущен {myself.username}')
        messages = await read_all_messages(channel_names[0])
        #print(len(messages))
        #for message in messages:
        #    print(message.get('message_text'))
        #break
        await post_video_in_channel(messages)
        print(f'Ожидаем {DELAY//60} минут')
        await asyncio.sleep(wait_time)


def check_connection():
    if not client.is_user_authorized():
        try:
            client.send_code_request(phone)
            me = client.sign_in(phone, input('Введите код: '))
        except SessionPasswordNeededError:
            password = input('Введите код 2фа: ')
            me = client.start(phone, password)

    return client.get_me()


if __name__ == '__main__':
    from handlers import *
    from db import *

    myself = check_connection()

    dp.loop.create_task(schedule(myself, DELAY))
    executor.start_polling(dp, on_startup=send_to_admin, loop=loop)
