import requests
import vk_api
import time
from datetime import date
from vk_api.longpoll import VkLongPoll, VkEventType
from random import randrange
import sqlalchemy


with open('VKtoken.txt', 'r') as file_object:
    vk_token = file_object.read().strip()

with open('group_token.txt', 'r') as file_object:
    group_token = file_object.read().strip()

with open('dbuser.txt', 'r') as file_object:
    bd_user = file_object.read().strip()

with open('dbpassword.txt', 'r') as file_object:
    bd_password = file_object.read().strip()

with open('dbname.txt', 'r') as file_object:
    bd_name = file_object.read().strip()

engine = sqlalchemy.create_engine(f'postgresql://{bd_user}:{bd_password}@localhost:5432/{bd_name}')
connection = engine.connect()

searching_params = {}
main_info = {}
people_ids = []
people_photo_url = []


class Bot:
    url = 'https://api.vk.com/method/'

    def __init__(self, token_vk, version):
        self.token_vk = token_vk
        self.version = version
        self.params = {
            'access_token': self.token_vk,
            'v': self.version
        }

    def user_main_info(self, user_id):
        time.sleep(1)

        user_main_info_url = self.url + 'users.get'
        user_main_info_params = {
            'user_ids': user_id,
            'fields': 'sex, city'
        }
        res = requests.get(user_main_info_url, params={**self.params, **user_main_info_params})
        res = res.json()
        info = res['response'][0]
        main_info['first_name'] = info['first_name']
        main_info['last_name'] = info['last_name']
        if info.get('sex') is None:
            main_info['sex'] = None
        else:
            if info['sex'] == 2:
                main_info['sex'] = 1
            elif info['sex'] == 1:
                main_info['sex'] = 2
            else:
                main_info['sex'] = 0
        if info.get('city') is None:
            main_info['city_id'] = None
        else:
            main_info['city_id'] = info['city']['id']

    def get_user_age(self, user_id):
        time.sleep(1)

        get_user_age_url = self.url + 'users.get'
        get_user_age_params = {
            'user_ids': user_id,
            'fields': 'bdate'
        }
        res = requests.get(get_user_age_url, params={**self.params, **get_user_age_params})
        res = res.json()
        info = res['response'][0]
        if info.get('bdate') is None:
            main_info['age_from'] = None
            main_info['age_to'] = None
        else:
            your_bdate = info['bdate']
            your_year = your_bdate[5:]
            today_year = str(date.today())
            today_year = today_year[:4]
            your_age = int(today_year) - int(your_year)
            main_info['age_from'] = your_age - 2
            main_info['age_to'] = your_age + 2

    def get_cities_id(self, city_name):
        time.sleep(1)

        get_cities_id_url = self.url + 'database.getCities'
        get_cities_id_params = {
            'country_id': 1,
            'need_all': 0
        }
        res = requests.get(get_cities_id_url, params={**self.params, **get_cities_id_params})
        res = res.json()
        city_names = res['response']['items']
        for city in city_names:
            if city['title'] == city_name:
                return city['id']

    def user_closed_open(self, user_id):
        time.sleep(1)

        user_closed_open_url = self.url + 'users.get'
        user_closed_open_params = {
            'user_ids': user_id
        }
        res = requests.get(user_closed_open_url, params={
            **self.params,
            **user_closed_open_params
        })
        res = res.json()
        return res['response'][0]['is_closed']

    def user_search_optimal_settings(self, offset, city_id, sex, age_from, age_to):
        time.sleep(1)

        user_search_optimal_settings_url = self.url + 'users.search'
        user_search_optimal_settings_params = {
            'offset': offset,
            'count': 1,
            'city': city_id,
            'sex': sex,
            'status': 6,
            'age_from': age_from,
            'age_to': age_to
        }
        res = requests.get(user_search_optimal_settings_url, params={
            **self.params,
            **user_search_optimal_settings_params
        })
        res = res.json()
        user_info = res['response']['items']
        while len(user_info) == 0:
            user_search_optimal_settings_params = {
                'offset': offset,
                'count': 1,
                'city': city_id,
                'sex': sex,
                'status': 6,
                'age_from': age_from,
                'age_to': age_to
            }
            res = requests.get(user_search_optimal_settings_url, params={
                **self.params,
                **user_search_optimal_settings_params
            })
            res = res.json()
            user_info = res['response']['items']
        user_info = user_info[0]['id']
        return user_info

    def user_search_you_setting(self, offset, city_id, sex, age_from, age_to):
        time.sleep(1)

        user_search_you_setting_url = self.url + 'users.search'
        user_search_you_setting_params = {
            'offset': offset,
            'count': 1,
            'city': city_id,
            'sex': sex,
            'status': 6,
            'age_from': age_from,
            'age_to': age_to
        }
        res = requests.get(user_search_you_setting_url, params={
            **self.params,
            **user_search_you_setting_params
        })
        res = res.json()
        user_info = res['response']['items']
        while len(user_info) == 0:
            user_search_you_setting_params = {
                'offset': offset,
                'count': 1,
                'city': city_id,
                'sex': sex,
                'status': 6,
                'age_from': age_from,
                'age_to': age_to
            }
            res = requests.get(user_search_you_setting_url, params={
                **self.params,
                **user_search_you_setting_params
            })
            res = res.json()
            user_info = res['response']['items']
        user_info = user_info[0]['id']
        return user_info

    def get_user_photo(self, user_id):
        time.sleep(3)

        top_photo = {}

        get_user_photo_url = self.url + 'photos.get'
        get_user_photo_params = {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1
        }
        res = requests.get(get_user_photo_url, params={
            **self.params,
            **get_user_photo_params
        })
        res = res.json()
        photo_info = res['response']['items']
        for photo in photo_info:
            top_photo[photo['sizes'][-1]['url']] = photo['likes']['count']
        inverse = [(meaning, social) for social, meaning in top_photo.items()]
        sorted_top_photos = sorted(inverse, reverse=True)
        top = sorted_top_photos[0:3]
        people_photo_url.clear()
        for photos in top:
            people_photo_url.append(photos[1])


bot_vk = Bot(vk_token, '5.126')


def write_msg(user_id, message):

    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


def checking_exciting_table_bd_user_search(user_id):

    exists_users = []
    info = connection.execute("""SELECT * FROM user_search;""").fetchall()
    for user_ids in info:
        exists_users.append(user_ids[1])
    if user_id in exists_users:
        write_msg(searching_params['user_id_answer'], f'Отлично, ты хочешь найти новых знакомых для себя,'
                                                      f'я могу предложить два варианта поиска:\n'
                                                      f'если интересует быстрый поиск просто введи '
                                                      f'- быстрый поиск '
                                                      f'и в ответ я пришлю тебе ссылку на аккаунт '
                                                      f'и топ 3 фото профиля\n'
                                                      f'если же интересует детальный поиск просто введи '
                                                      f'и в ответ я пришлю тебе ссылку на аккаунт '
                                                      f'и топ 3 фото профиля')
    else:
        write_msg(searching_params['user_id_answer'], f'Отлично, ты хочешь найти новых знакомых для себя,'
                                                      f'я могу предложить два варианта поиска:\n'
                                                      f'если интересует быстрый поиск просто введи '
                                                      f'- быстрый поиск '
                                                      f'и в ответ я пришлю тебе ссылку на аккаунт '
                                                      f'и топ 3 фото профиля\n'
                                                      f'если же интересует детальный поиск просто введи '
                                                      f'и в ответ я пришлю тебе ссылку на аккаунт '
                                                      f'и топ 3 фото профиля')
        add_info_in_table_user_search(user_id)


def add_info_in_table_user_search(user_id):

    connection.execute(
        f"""INSERT INTO User_search (user_id, user_url) VALUES ('{user_id}', 'https://vk.com/id{user_id}');"""
    )


def fast_searching_exists(user_id):

    if main_info['sex'] is None or \
            main_info['city_id'] is None or \
            main_info['age_from'] is None or \
            main_info['age_to'] is None:
        return False
    else:
        searching_params['offset'] = 0
        list_for_checking = checking_exciting_in_table_vk_user_fast_search(user_id)
        if bot_vk.user_search_optimal_settings(
                searching_params['offset'],
                main_info['city_id'], main_info['sex'],
                main_info['age_from'], main_info['age_to']) in list_for_checking:
            pass
        return True


def fast_searching_not_exists():

    people_ids_not_exist_in_bd = bot_vk.user_search_optimal_settings(
        searching_params['offset'],
        main_info['city_id'],
        main_info['sex'],
        main_info['age_from'],
        main_info['age_to'])
    if bot_vk.user_closed_open(people_ids_not_exist_in_bd) is False:
        bot_vk.get_user_photo(people_ids_not_exist_in_bd)
        for each_photo in people_photo_url:
            write_msg(searching_params['user_id_answer'], f'{each_photo}')
        write_msg(searching_params['user_id_answer'], f'https://vk.com/id{people_ids_not_exist_in_bd}')
    elif bot_vk.user_closed_open(people_ids_not_exist_in_bd) is True:
        write_msg(searching_params['user_id_answer'], f'vk.com/id{people_ids_not_exist_in_bd}, '
                                                      f'к сожелению это закрытый профиль '
                                                      f'и я не могу отправить тебе его или ее фото.')
    add_info_in_vk_user_fast_search(people_ids_not_exist_in_bd)
    write_msg(event.user_id, 'Если хочешь просмотреть следующий результат просто введи еще.\n'
                             'Если хочешь вернуться к началу просто введи начало')


def detail_searching_exists(user_id):

    searching_params['offset'] = 0
    list_for_checking = checking_exciting_in_table_vk_user_detail_search(user_id)
    if bot_vk.user_search_you_setting(searching_params['offset'],
                                      searching_params['city_id'],
                                      searching_params['sex'],
                                      searching_params['age_from'],
                                      searching_params['age_to']) in list_for_checking:
        pass
    return True


def detail_searching_not_exists():

    people_ids_not_exist_in_bd = bot_vk.user_search_you_setting(searching_params['offset'],
                                                                searching_params['city_id'],
                                                                searching_params['sex'],
                                                                searching_params['age_from'],
                                                                searching_params['age_to'])
    if bot_vk.user_closed_open(people_ids_not_exist_in_bd) is False:
        bot_vk.get_user_photo(people_ids_not_exist_in_bd)
        for each_photo in people_photo_url:
            write_msg(searching_params['user_id_answer'], f'{each_photo}')
        write_msg(searching_params['user_id_answer'], f'https://vk.com/id{people_ids_not_exist_in_bd}')
    elif bot_vk.user_closed_open(people_ids_not_exist_in_bd) is True:
        write_msg(searching_params['user_id_answer'], f'vk.com/id{people_ids_not_exist_in_bd}, '
                                                      f'к сожелению это закрытый профиль '
                                                      f'и я не могу отправить тебе его или ее фото.')
    add_info_in_vk_user_detail_search(people_ids_not_exist_in_bd)
    write_msg(event.user_id, 'Если хочешь просмотреть следующий результат просто введи еще.\n'
                             'Если хочешь вернуться к началу просто введи начало')


def checking_exciting_in_table_vk_user_fast_search(user_id):

    exists_users = []
    info = connection.execute(
        f"""SELECT * FROM vk_user_fast_search WHERE user_search_id = {user_id};"""
    ).fetchall()
    for user_ids in info:
        exists_users.append(user_ids[3])
    return exists_users


def checking_exciting_in_table_vk_user_detail_search(user_id):

    exists_users = []
    info = connection.execute(
        f"""SELECT * FROM vk_user_detail_search WHERE user_search_id = {user_id};"""
    ).fetchall()
    for user_ids in info:
        exists_users.append(user_ids[3])
    return exists_users


def add_info_in_vk_user_fast_search(user_id):

    bot_vk.user_main_info(user_id)
    connection.execute(
        f"""INSERT INTO vk_user_fast_search (user_first_name, user_second_name, user_id, user_url, user_search_id) VALUES ('{main_info['first_name']}', '{main_info['last_name']}', '{user_id}', 'https://vk.com/id{user_id}', '{searching_params['user_id']}');""")


def add_info_in_vk_user_detail_search(user_id):

    bot_vk.user_main_info(user_id)
    connection.execute(
        f"""INSERT INTO vk_user_detail_search (user_first_name, user_second_name, user_id, user_url, user_search_id) VALUES ('{main_info['first_name']}', '{main_info['last_name']}', '{user_id}', 'https://vk.com/id{user_id}', '{searching_params['user_id']}');""")


def listen():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                return event.text

vk = vk_api.VkApi(token=group_token)
longpoll = VkLongPoll(vk)

for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            request = event.text
            if request == 'Привет' or request == 'привет' or request == 'Хай' or request == 'хай':
                write_msg(event.user_id, f'Привет это бот - vkinder по поиску людей.\n'
                                         f'Для кого ты хочешь найти подходящих людей?\n'
                                         f'если ты хочешь найти для себя просто напиши - для себя,\n '
                                         f'а если ты хочешь найти для друга введи - для друга')
            elif request == 'для себя':
                searching_params['user_id_answer'] = event.user_id
                searching_params['user_id'] = event.user_id
                checking_exciting_table_bd_user_search(searching_params['user_id'])
            elif request == 'для друга':
                write_msg(event.user_id, f'Отлично просто напиши мне id его аккаунта.')
                request = listen()
                searching_params['user_id_answer'] = event.user_id
                checking_exciting_table_bd_user_search(int(request))
            elif request == 'быстрый поиск':
                bot_vk.user_main_info(searching_params['user_id'])
                bot_vk.get_user_age(searching_params['user_id'])
                answer_for_exists = fast_searching_exists(searching_params['user_id'])
                if answer_for_exists is False:
                    write_msg(event.user_id, 'Часть информации отсутствует, рекомендую использовать детальный поиск.')
                elif answer_for_exists is True:
                    check_list = checking_exciting_in_table_vk_user_fast_search(searching_params['user_id'])
                    searching_params['offset'] += len(check_list)
                    fast_searching_not_exists()
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            if event.to_me:
                                request = event.text
                                if request == 'начало':
                                    write_msg(event.user_id, f'Привет это бот - vkinder по поиску людей.\n'
                                                             f'Для кого ты хочешь найти подходящих людей?\n'
                                                             f'если ты хочешь найти для себя просто напиши - для себя,\n '
                                                             f'а если ты хочешь найти для друга введи - для друга')
                                    break
                                elif request == 'еще':
                                    check_list = checking_exciting_in_table_vk_user_fast_search(
                                        searching_params['user_id'])
                                    searching_params['offset'] += len(check_list)
                                    fast_searching_not_exists()
                                else:
                                    write_msg(event.user_id, f'Не знаю такой комманды')
            elif request == 'детальный поиск':
                write_msg(event.user_id, f'Отлично, давай тогда определися с несколькими параметрами.\n'
                                         f'Для начала давай определимся какого пола ты хочешь найти людей.\n'
                                         f'Мужского\n'
                                         f'Женского\n'
                                         f'Не имеет значения')
            elif request == 'Мужского' or request == 'мужского':
                searching_params['sex'] = 2
                write_msg(event.user_id, f'Отлично, тепрерь перейдем к городу, в каком городе ты хочешь найти людей?')
                info_city_from_user = listen()
                searching_params['city_id'] = bot_vk.get_cities_id(info_city_from_user)
                if searching_params['city_id'] is None:
                    write_msg(event.user_id, f'Не знаю такого города')
                else:
                    write_msg(event.user_id, f'{info_city_from_user}, красивый город, '
                                             f'осталось лишь с возрастным диапозоном поиска.\n'
                                             f'Для начала укажи минимальны возраст '
                                             f'с которого надо начать поиск.')
                info_age_from_user = listen()
                searching_params['age_from'] = info_age_from_user
                write_msg(event.user_id, f'ну и на полследок укажи максимальный возраст.')
                info_age_to_user = listen()
                searching_params['age_to'] = info_age_to_user
                answer_for_exists = detail_searching_exists(
                    searching_params['user_id'])
                if answer_for_exists is True:
                    check_list = checking_exciting_in_table_vk_user_detail_search(
                        searching_params['user_id'])
                    searching_params['offset'] += len(check_list)
                    detail_searching_not_exists()
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            if event.to_me:
                                request = event.text
                                if request == 'начало':
                                    write_msg(event.user_id, f'Привет это бот - vkinder по поиску людей.\n'
                                                             f'Для кого ты хочешь найти подходящих людей?\n'
                                                             f'если ты хочешь найти для себя просто напиши - для себя,\n '
                                                             f'а если ты хочешь найти для друга введи - для друга')
                                    break
                                elif request == 'еще':
                                    check_list = checking_exciting_in_table_vk_user_fast_search(
                                        searching_params['user_id'])
                                    searching_params['offset'] += len(check_list)
                                    fast_searching_not_exists()
                                else:
                                    write_msg(event.user_id, f'Не знаю такой комманды')
            elif request == 'Женского' or request == 'женского':
                searching_params['sex'] = 1
                write_msg(event.user_id, f'Отлично, тепрерь перейдем к городу, в каком городе ты хочешь найти людей?')
                info_city_from_user = listen()
                searching_params['city_id'] = bot_vk.get_cities_id(info_city_from_user)
                if searching_params['city_id'] is None:
                    write_msg(event.user_id, f'Не знаю такого города')
                else:
                    write_msg(event.user_id, f'{info_city_from_user}, красивый город, '
                                             f'осталось лишь с возрастным диапозоном поиска.\n'
                                             f'Для начала укажи минимальны возраст '
                                             f'с которого надо начать поиск.')
                info_age_from_user = listen()
                searching_params['age_from'] = info_age_from_user
                write_msg(event.user_id, f'ну и на полследок укажи максимальный возраст.')
                info_age_to_user = listen()
                searching_params['age_to'] = info_age_to_user
                answer_for_exists = detail_searching_exists(
                    searching_params['user_id'])
                if answer_for_exists is True:
                    check_list = checking_exciting_in_table_vk_user_detail_search(
                        searching_params['user_id'])
                    searching_params['offset'] += len(check_list)
                    detail_searching_not_exists()
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            if event.to_me:
                                request = event.text
                                if request == 'начало':
                                    write_msg(event.user_id, f'Привет это бот - vkinder по поиску людей.\n'
                                                             f'Для кого ты хочешь найти подходящих людей?\n'
                                                             f'если ты хочешь найти для себя просто напиши - для себя,\n '
                                                             f'а если ты хочешь найти для друга введи - для друга')
                                    break
                                elif request == 'еще':
                                    check_list = checking_exciting_in_table_vk_user_fast_search(
                                        searching_params['user_id'])
                                    searching_params['offset'] += len(check_list)
                                    fast_searching_not_exists()
                                else:
                                    write_msg(event.user_id, f'Не знаю такой комманды')
            elif request == 'Не имеет значения' or request == 'не имеет значения':
                searching_params['sex'] = 0
                write_msg(event.user_id, f'Отлично, тепрерь перейдем к городу, в каком городе ты хочешь найти людей?')
                info_city_from_user = listen()
                searching_params['city_id'] = bot_vk.get_cities_id(info_city_from_user)
                if searching_params['city_id'] is None:
                    write_msg(event.user_id, f'Не знаю такого города')
                else:
                    write_msg(event.user_id, f'{info_city_from_user}, красивый город, '
                                             f'осталось лишь с возрастным диапозоном поиска.\n'
                                             f'Для начала укажи минимальны возраст '
                                             f'с которого надо начать поиск.')
                info_age_from_user = listen()
                searching_params['age_from'] = info_age_from_user
                write_msg(event.user_id, f'ну и на полследок укажи максимальный возраст.')
                info_age_to_user = listen()
                searching_params['age_to'] = info_age_to_user
                answer_for_exists = detail_searching_exists(
                    searching_params['user_id'])
                if answer_for_exists is True:
                    check_list = checking_exciting_in_table_vk_user_detail_search(
                        searching_params['user_id'])
                    searching_params['offset'] += len(check_list)
                    detail_searching_not_exists()
                    for event in longpoll.listen():
                        if event.type == VkEventType.MESSAGE_NEW:
                            if event.to_me:
                                request = event.text
                                if request == 'начало':
                                    write_msg(event.user_id, f'Привет это бот - vkinder по поиску людей.\n'
                                                             f'Для кого ты хочешь найти подходящих людей?\n'
                                                             f'если ты хочешь найти для себя просто напиши - для себя,\n '
                                                             f'а если ты хочешь найти для друга введи - для друга')
                                    break
                                elif request == 'еще':
                                    check_list = checking_exciting_in_table_vk_user_fast_search(
                                        searching_params['user_id'])
                                    searching_params['offset'] += len(check_list)
                                    fast_searching_not_exists()
                                else:
                                    write_msg(event.user_id, f'Не знаю такой комманды')
            else:
                write_msg(event.user_id, 'не понял, потоврите запрос.')
