import sqlite3
import os

db_name = "db/videos.db"
conn_videos = sqlite3.connect(db_name)
cursor_videos = conn_videos.cursor()
# Проверяем наличие БД и создаем, если ее нет
if os.path.exists(db_name):
    # Создание таблицы
    cursor_videos.execute("""CREATE TABLE IF NOT EXISTS videos
                (id integer PRIMARY KEY, title text, num_from_site text, date text, user_id text, downloaded text, uploaded text, file_id text)
                """)
    conn_videos.commit()
    print(f'Таблица {db_name} создана')

    # Создание таблицы users
    cursor_videos.execute("""CREATE TABLE IF NOT EXISTS users
                      (user_id TEXT PRIMARY KEY, username text, first_name text, last_name text)
                   """)
    conn_videos.commit()
    print(f'Таблица {db_name} создана')


# добавление видео
async def add_videos(id=None, title=None, num_from_site=None, date=None, to_chat=None, downloaded='False', uploaded='False', file_id=None):
    global conn_videos
    global cursor_videos

    id = cursor_videos.lastrowid
    table = 'videos'
    cursor_videos.execute(f"""
                    INSERT INTO {table}
                    VALUES ('{id+1}', '{title}', '{num_from_site}', '{date}', '{to_chat}', '{downloaded}', '{uploaded}', '{file_id}')
                """)
    try:
        conn_videos.commit()
    except Exception as e:
        print(e.args)
    else:
        print(f'Запись {title} = {num_from_site} добавлена в БД!')
        return True


# добавление пользователя
async def add_user(user_id=None, username=None, first_name=None, last_name=None):
    """
    user_id TEXT PRIMARY KEY, username text, firstname text, lastname text
    """
    global conn_videos
    global cursor_videos

    table = 'users'
    cursor_videos.execute(f"""
                    INSERT INTO {table}
                    VALUES ('{user_id}', '{username}', '{first_name}', '{last_name}')
                """)
    try:
        conn_videos.commit()
    except Exception as e:
        print(e.args)
    else:
        print(f'Запись {user_id} - {username} добавлена в БД!')
        return True


# чтение
async def read_from_db(table='videos', field=None, value=None):
    global conn_videos
    global cursor_videos

    request = f"SELECT * FROM {table} WHERE {field}='{value}'"
    try:
        cursor_videos.execute(request)
    except Exception as e:
        print(e.args)
        return

    return cursor_videos.fetchall()


async def read_user(table='users', user_id=None):
    result = await read_from_db(table=table, field='user_id', value=user_id)
    if result:
        return result
    else:
        return False


# поля  id integer
#       title text
#       num_from_site text
#       date text
#       to_chat text

# поиск названия
async def read_title(table='videos', title=None):
    result = await read_from_db(table=table, field='title', value=title)
    if result:
        return result
    else:
        return


# поиск по номеру файла с сайта
async def read_num_from_site(table='videos', num_from_site=None):
    result = await read_from_db(table=table, field='num_from_site', value=num_from_site)
    if result:
        return result
    else:
        return


# поиск по номеру чата
async def read_to_chat(table='videos', to_chat=None):
    result = await read_from_db(table=table, field='to_chat', value=to_chat)
    if result:
        return result
    else:
        return


# обновление статусов
async def update_download(table='videos', num_from_site=None, value='True'):
    global conn_videos
    global cursor_videos
    field = 'num_from_site'

    request = f"UPDATE {table} " \
              f"SET downloaded='{value}' " \
              f"WHERE {field}='{num_from_site}'"
    try:
        cursor_videos.execute(request)
    except Exception as e:
        print(f'Не смогли обновить статус загружено! для файла {num_from_site}')
        print(f'Ошибка: {e.args}')
        return False
    return True


async def update_upload(table='videos', field='num_from_site', field_value=None, value='True', file_id=None):
    global conn_videos
    global cursor_videos

    request = f"UPDATE {table} " \
              f"SET uploaded='{value}', file_id='{file_id}' " \
              f"WHERE {field}='{field_value}'"
    try:
        cursor_videos.execute(request)
    except Exception as e:
        print(f'Не смогли обновить статус загружено! для файла {field_value}')
        print(f'Ошибка: {e.args}')
        return False
    return True
