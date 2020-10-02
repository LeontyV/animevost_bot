import asyncio
import os

from telethon import TelegramClient, events, sync
from aiogram import Bot, Dispatcher, executor
from config import BOT_TOKEN, api_id, api_hash, phone
from telethon.errors import SessionPasswordNeededError

# задаем время повторения задания
DELAY = 3600

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
client = TelegramClient('session/'+phone, api_id, api_hash)
client.connect()


async def schedule(myself, wait_time):
    while True:
        print(f'Работает {myself.username}')
        # client.send_message('Leonty', f'Запущен {myself.username}')
        await post_video_in_channel()
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
