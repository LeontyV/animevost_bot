import sqlite3
import os

db_name = "db/videos.db"
conn_videos = sqlite3.connect(db_name)  # или :memory: чтобы сохранить в RAM
cursor_videos = conn_videos.cursor()
# создаем базу для расходов
if os.path.exists(db_name):
    # Создание таблицы
    cursor_videos.execute("""CREATE TABLE IF NOT EXISTS videos
                      (id integer, title text, num_from_site text, date text, to_chat text)
                   """)
    conn_videos.commit()
    print(f'Таблица {db_name} создана')

    # Создание таблицы users
    cursor_videos.execute("""CREATE TABLE IF NOT EXISTS users
                      (user_id TEXT PRIMARY KEY, name text)
                   """)
    conn_videos.commit()
    print(f'Таблица {db_name} создана')


# добавление видео
def add_videos(id=None, title=None, num_from_site=None, date=None, to_chat=None):
    global conn_videos
    global cursor_videos

    table = 'videos'
    cursor_videos.execute(f"""
                    INSERT INTO {table}
                    VALUES ('{title}', '{num_from_site}', '{date}', '{to_chat}')
                """)
    try:
        conn_videos.commit()
    except Exception as e:
        print(e.args)
    else:
        print(f'Запись {title} = {num_from_site} добавлена в БД!')
        return True


# чтение видео
def read_from_db(table=None, field=None, value=None):
    global conn_videos
    global cursor_videos
    table = 'videos'

    request = f"SELECT * FROM {table} WHERE {field}='{value}'"
    try:
        cursor_videos.execute(request)
    except Exception as e:
        print(e.args)
        return

    return cursor_videos.fetchall()


# поля  id integer
#       title text
#       num_from_site text
#       date text
#       to_chat text


# поиск названия
def read_title(table, title):
    result = read_from_db(table=table, field='title', value=title)
    if result:
        return result
    else:
        return


# поиск по номеру файла с сайта
def read_date(table, num_from_site):
    result = read_from_db(table=table, field='num_from_site', value=num_from_site)
    if result:
        return result
    else:
        return


# поиск по номеру чата
def read_who(table, to_chat):
    result = read_from_db(table=table, field='to_chat', value=to_chat)
    if result:
        return result
    else:
        return