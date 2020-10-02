import json
import os
import re
from datetime import datetime as dt

import asyncio
from lxml import etree

from config import url, anime_list
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

async def get_animes():
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


def compare_dates(date):
    time_now = dt.now()


def filter_serie(a):
    b = []
    for elem in a:
        if 'серия' in elem:
            b.append(elem)

    return b


async def get_last_serie(anime_url, folder_name):
    api_url = 'https://a71.agorov.org/frame2.php?play='
    folder_name = folder_name.replace(':', '-')
    try:
        os.mkdir(folder_name)
    except NotADirectoryError:
        print(f'Уберите проблемные символы в имени {folder_name}')
    except OSError:
        print(f'Папка с таким именем {folder_name} уже существует!')

    r = RequestsWrapper()
    content = r.get_html_page(anime_url, tree=True)

    try:
        series_text = content.xpath('//script[contains(text(), "var data =")]/text()')[0]
        series_text = re.findall('var data = (.+);', series_text)[0]
    except IndexError:
        print('не нашли ссылку на список серий')
        return
    series_text = series_text.replace('\r', '')
    series_text = series_text.replace('\t', '')
    series_text = series_text.replace('\n', '')
    series_text = series_text.replace(',}', '}')
    series_json = json.loads(series_text)

    # название последней серии
    serie_name = [serie for serie in list(series_json) if 'серия' in serie][-1]
    # номер последней серии
    last_serie = str(series_json.get(serie_name))

    serie_name = f'{folder_name} ({serie_name})'
    api_url = api_url + last_serie

    video_frame = r.get_html_page(api_url)
    api_url = etree.fromstring(video_frame).get('src')
    video_frame = r.get_html_page(api_url, tree=True)

    download_link = video_frame.xpath('//a[contains(text(), "480")]/@href')[0]
    format_video = re.findall('([a-zA-Z0-9]+)\?', download_link)[0]
    serie_name += '.' + format_video
    if os.path.isfile(f'{folder_name}/{serie_name}'):
        print(f'файл с именем "{folder_name}/{serie_name}" уже существует!')
        return f'{folder_name}/{serie_name}', serie_name
    print(f'Скачиваем файл {serie_name} \nurl={download_link} \npage={api_url}')
    content = r.get(download_link)
    with open(f'./{folder_name}/{serie_name}', 'wb') as f:
        f.write(content.content)

    #return f'./{folder_name}/{serie_name}', serie_name
    #return download_link, serie_name
    #return content.content, serie_name


def get_timer(url):
    print(url)
    r = RequestsWrapper()
    content = r.get_html_page(url, tree=True)

    next_time = content.xpath('//script[contains(text(), "parseInt")]/text()')[0]
    next_time = re.findall('parseInt\((\d+) ', next_time)[0]
    print(dt.fromtimestamp(int(next_time)))


async def watcher():
    videos = []
    time_now = dt.now()
    day = time_now.today().weekday()
    key = list(DAYS)[day]
    animes = await get_animes()
    animes = animes.get(key) # тут список словарей
    #for anime_to_watch in anime_list:
    for anime in animes:
        #if anime_to_watch in anime.get('name'):
        url = anime.get('url')
        #get_timer(url)
        #get_timer('https://a71.agorov.org/tip/tv/1894-black-clover5.html')
        print(anime)
        video = await get_last_serie(url, anime.get('name'))
        if video:
            videos.append(video)

    #print(len(videos))
    return videos

#watcher()
#print(get_animes())
#get_last_serie('https://a71.agorov.org/tip/tv/1805-boruto-naruto-next-generations1112.html', 'boruto')