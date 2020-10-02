import asyncio
import os

from telethon import TelegramClient, events, sync
from aiogram import Bot, Dispatcher, executor
from config import BOT_TOKEN, api_id, api_hash, phone
from telethon.errors import SessionPasswordNeededError

DELAY = 60

loop = asyncio.get_event_loop()
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")

dp = Dispatcher(bot, loop=loop)

if not os.path.exists('session'):
    os.makedirs('session')

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

    myself = check_connection()

    dp.loop.create_task(schedule(myself, DELAY))
    executor.start_polling(dp, on_startup=send_to_admin, loop=loop)

"""
DELAY = 24*3600

loop = asyncio.get_event_loop()
bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, loop=loop)


async def schedule(wait_time):
	while True:
		answer = await crl_to_tlgrm()
		for crl in answer.values():
			if 'ALERT' in crl:
				await bot.send_message(chat_id=uc_chat_id, text=f'<b>{crl}</b>', parse_mode='HTML')
			elif crl == '':
				await bot.send_message(chat_id=uc_chat_id, text=f'404 файл не найден!!!', parse_mode='HTML')
			else:
				await bot.send_message(chat_id=uc_chat_id, text=f'<b>{crl}</b>', parse_mode='HTML')
		await asyncio.sleep(wait_time)

	
if __name__ == '__main__':
	from handlers import *
	loop.create_task(schedule(DELAY)) # в идеале 3600
	executor.start_polling(dp, on_startup=send_to_admin, loop=loop)
"""