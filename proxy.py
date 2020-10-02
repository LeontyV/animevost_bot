from random import choice


def get_random_ua():
    """
    Возвращает строку случайного UserAgent или None.
    :return: строка UserAgent.
    """
    user_agents = open('firefox.txt').read().split('\n')
    ua = choice(user_agents)
    try:
        return ua
    except TypeError:
        return None
