from aiogram import types
from keyboards import ListOfButtons
from config import admin_id, chat_ids, accepted_users
from filters import *
from main import bot, dp, client
from datetime import datetime as dt
from animevost_parser import *


async def send_to_admin(*args):
    """
    Отправляем сообщение Админу
    """
    me = await bot.get_me()
    print(me.username)
    # await bot.send_message(chat_id=admin_id, text="Бот запущен: " + me.username)
    # await bot.send_message(chat_id=admin_id, text='Нажми: /menu /start')


async def check_users(user):
    if user in accepted_users:
        return True
    else:
        print(f'{user} попытался обратиться к боту!')
        return False


@dp.channel_post_handler(regexp='/[Ss]tart')
async def echo(message: types.Message):
    chat_id = str(message.chat.id)
    if chat_id in chat_ids:
        username = message.chat.username
        text = f'Привет, {username}!\nДля вывода расписания набери команду - /start.'
        await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')
        await post_in_channel()
    else:
        text = f'id={chat_id} не в списке разрешенных.'
        await bot.send_message(chat_id=chat_id, text=text)


@dp.message_handler(regexp='/[Ss]tart')
async def echo(message: types.Message):
    print(message)
    chat_id = message.chat.id
    username = message.chat.username
    user_exists = await read_user(user_id=str(chat_id))
    if not user_exists:
        await add_user(user_id=str(chat_id),
                       username=str(username),
                       first_name=str(message.chat.first_name),
                       last_name=str(message.chat.last_name))
    text = f'Привет, {username}!\nДля вывода расписания набери команду - /start.'
    await bot.send_message(chat_id=chat_id, text=text, parse_mode='HTML')


async def post_in_channel():
    for chat_id in chat_ids:
        days = get_animes()
        for key in days.keys():
            animes = days.get(key)
            if DAYS.get(key):
                day_name = DAYS.get(key)
                text = f'<b>Расписание на {day_name}:</b>'
                for anime in animes:
                    text = text + f'\n    - <a href="{anime.get("url")}">{anime.get("name")}</a>'
                await bot.send_message(chat_id=chat_id, text=text, parse_mode='html', disable_web_page_preview=True)


# @dp.channel_post_handler(regexp='/[Nn]ow')
async def post_video_in_channel():  # (message: types.Message):
    for chat_id in chat_ids:
        videos = await watcher()
        await add_videos(title=videos[1], num_from_site=videos[2], date=str(dt.now()), to_chat=chat_id)
        await update_download(num_from_site=videos[2])
        for video in videos:
            print(f'Отправляем {video[1]}')
            # me = await bot.get_me()
            await client.send_file(int(chat_id), video[0], filename=video[1])
            print(f'Файл {video[1]} отправлен!')
