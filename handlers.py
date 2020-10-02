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


@dp.channel_post_handler(content_types=['text', 'video'])
async def pick_up(message: types.Message):
    await update_upload(field='title', field_value=str(message.caption), file_id=str(message.video.file_id))
    print(message)


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


async def post_video_in_channel():
    for chat_id in chat_ids:
        await watcher(chat_id)
