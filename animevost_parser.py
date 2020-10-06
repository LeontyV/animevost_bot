import json
import os
import re
from datetime import datetime as dt
import math

from moviepy.editor import VideoFileClip
from telethon.tl.types import DocumentAttributeVideo
from tqdm import tqdm
import asyncio
from lxml import etree
from requests.exceptions import ConnectionError

from config import url, anime_list
from db import *
from main import client
from requests_wrapper import RequestsWrapper

DAYS = {
    'raspisMon': 'Понедельник',
    'raspisTue': 'Вторник',
    'raspisWed': 'Среда',
    'raspisThu': 'Четверг',
    'raspisFri': 'Пятница',
    'raspisSat': 'Суббота',
    'raspisSun': 'Воскресенье',
}


def clean_text(text):
    text = text.replace('\r', '')
    text = text.replace('\t', '')
    text = text.replace('\n', '')
    return text


def get_animes():
    afisha = {}

    r = RequestsWrapper()
    content = r.get_html_page(url, tree=True)

    week_days = content.xpath('//div[@class="raspis"]')
    for day in week_days:
        id = {day.get('id'): []}
        animes_in_day = day.xpath('.//a')
        for anime in animes_in_day:
            anime_url = anime.get('href')
            anime_url = url + anime_url
            anime_name = anime.text
            id[day.get('id')].append({
                'name': anime_name,
                'url': anime_url,
            })
        afisha.update(id)

    return afisha


async def get_last_serie(anime_url, folder_name):
    api_url = 'https://a71.agorov.org/frame2.php?play='
    folder_name = folder_name.replace(':', '-')
    folder_name = re.findall('^([ёЁА-яа-я,.\s-]+)', folder_name)[0]
    folder_name = folder_name.strip()
    folder_path = f'video/{folder_name}'
    try:
        os.mkdir(folder_path)
    except NotADirectoryError:
        print(f'Уберите проблемные символы в имени "{folder_path}"')
    except OSError:
        print(f'Папка с таким именем "{folder_path}" уже существует!')

    r = RequestsWrapper()
    content = r.get_html_page(anime_url, tree=True)

    try:
        series_text = content.xpath('//script[contains(text(), "var data =")]/text()')[0]
        series_text = re.findall('var data = (.+);', series_text)[0]
    except IndexError:
        print('не нашли ссылку на список серий')
        return
    series_text = clean_text(series_text)
    series_text = series_text.replace(',}', '}')
    series_json = json.loads(series_text)

    # название последней серии
    serie_name = [serie for serie in list(series_json) if 'серия' in serie][-1]
    # номер последней серии
    last_serie = str(series_json.get(serie_name))
    # проверка наличия уже такого файла
    check_serie = await read_num_from_site(num_from_site=last_serie)
    need_to_download = True
    need_to_upload = True
    if check_serie is not None:
        check_serie = check_serie[0]
        print(check_serie)
        if check_serie[5] == 'True':
            print(f'Нашли серию в базе и она уже скачана.')
            need_to_download = False
            if check_serie[6] == 'True':
                need_to_upload = False

    serie_name = f'{folder_name} ({serie_name})'
    api_url = api_url + last_serie

    video_frame = r.get_html_page(api_url)
    api_url = etree.fromstring(video_frame).get('src')
    video_frame = r.get_html_page(api_url, tree=True)

    download_link = video_frame.xpath('//a[contains(text(), "480")]/@href')[0]
    format_video = re.findall('([a-zA-Z0-9]+)\?', download_link)[0]
    serie_name += '.' + format_video
    file_path = f'{folder_path}/{serie_name}'
    file_path = clean_text(file_path)

    return download_link, serie_name, last_serie, file_path, need_to_download, need_to_upload


async def watcher(chat_id, messages):
    time_now = dt.now()
    day = time_now.today().weekday()
    key = list(DAYS)[day]  # забирает ключ для текущего дня
    animes = get_animes()

    for key in DAYS:  # если нужно перебрать всю неделю, а не текущий день
        anime_list = animes.get(key)  # тут список словарей
        for anime in anime_list:
            print(f'\nПроверяем {anime.get("name")}')
            url = anime.get('url')
            video_info = await get_last_serie(url, anime.get('name'))
            if type(video_info) is tuple:
                file_link = video_info[0]
                file_name = video_info[1]
                file_uid = video_info[2]
                file_path = video_info[3]
                need_download = video_info[4]
                need_to_upload = video_info[5]
                message_id = 0
                for message in messages:
                    if file_name == message.get('message_text'):
                        message_id = message.get('message_id')
                        need_to_upload = False
                        print(f'Файл {file_name} уже отправлен на канал!')
                        await add_videos(id=message_id, title=file_name, num_from_site=file_uid, date=str(dt.now()),
                                         to_chat=chat_id,
                                         downloaded='True')
                        if await update_upload(field_value=file_uid, file_id=str(message.get('media_id'))):
                            print(f'Успешно обновили {file_name} - {file_uid}')

                if need_download:
                    await download_file(file_link, file_name, file_path, file_uid)
                    await add_videos(id=message_id, title=file_name, num_from_site=file_uid, date=str(dt.now()),
                                     to_chat=chat_id,
                                     downloaded='True')
                    await update_download(num_from_site=file_uid)

                if need_to_upload:
                    print(f'Отправляем {file_name}')
                    # me = await bot.get_me()
                    try:
                        clip = VideoFileClip(file_path)
                    except OSError:
                        print(f'Ошибка открытия файла {file_name}')
                        os.remove(file_path)
                        continue
                    duration = int(clip.duration)
                    try:
                        await client.send_file(int(chat_id), file_path, filename=file_name, caption=file_name, attributes=(DocumentAttributeVideo(duration, 800, 560),))
                    except sqlite3.OperationalError:
                        print(f'чет база залочена!')
                        continue
                    print(f'Файл {file_name} отправлен!')
                    await update_upload(field_value=file_uid)


async def download_file(download_link, serie_name, file_path, file_uid):
    total_size = 0
    wrote = 0
    for _ in range(5):
        r = RequestsWrapper()
        if os.path.isfile(file_path):
            print(f'\nФайл с именем "{serie_name}" уже существует!')
            return file_path, serie_name
        print(f'\nСкачиваем файл "{serie_name}" \n\turl={download_link}')
        for _ in range(5):
            try:
                content = r.get(download_link, stream=True)
            except ConnectionError:
                print('Ошибка соединения. Нас отвергли! Пробуем ещё!')
                continue
            break

        total_size = int(content.headers.get('content-length', 0));
        block_size = 1024
        wrote = 0
        with open(file_path, 'wb') as f:
            for data in tqdm(content.iter_content(block_size), total=math.ceil(total_size // block_size), unit='KB',
                             unit_scale=True):
                wrote = wrote + len(data)
                f.write(data)

        if total_size != 0 and wrote != total_size:
            print("Ошибка! Файл не сохранился.")
            continue
        else:
            break

    if total_size != 0 and wrote != total_size:
        print("Ошибка! Файл после 5 попыток даже не сохранился.")
        return False

    return True
