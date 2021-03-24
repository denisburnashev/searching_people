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

main_info = {}
people_found_info = {}
result = {}
people_ids = []
people_photo_url = []
searching_params = {}


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
        print(main_info)

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

    def user_search_optimal_settings(self, city_id, sex, age_from, age_to):
        random_people = randrange(1, 1000)
        searching_params['offset'] = random_people

        user_search_optimal_settings_url = self.url + 'users.search'
        user_search_optimal_settings_params = {
            'offset': searching_params['offset'],
            'count': 1,
            'city': city_id,
            'sex': sex,
            'status': 6,
            'age_from': age_from,
            'age_to': age_to
        }
        time.sleep(1)
        res = requests.get(user_search_optimal_settings_url, params={
            **self.params,
            **user_search_optimal_settings_params
        })
        res = res.json()
        print(res)
        user_info = res['response']['items']
        if len(user_info) == 0:
            return False
        else:
            result['user_result'] = user_info[0]['id']
            people_found_info['first_name'] = user_info[0]['first_name']
            people_found_info['last_name'] = user_info[0]['last_name']
            return True

    def user_search_you_setting(self, city_id, sex, age_from, age_to):
        random_people = randrange(1, 1000)
        searching_params['offset'] = random_people

        user_search_you_setting_url = self.url + 'users.search'
        user_search_you_setting_params = {
            'offset': searching_params['offset'],
            'count': 1,
            'city': city_id,
            'sex': sex,
            'status': 6,
            'age_from': age_from,
            'age_to': age_to
        }
        time.sleep(1)
        res = requests.get(user_search_you_setting_url, params={
            **self.params,
            **user_search_you_setting_params
        })
        res = res.json()
        print(res)
        user_info = res['response']['items']
        if len(user_info) == 0:
            return False
        else:
            result['user_result'] = user_info[0]['id']
            people_found_info['first_name'] = user_info[0]['first_name']
            people_found_info['last_name'] = user_info[0]['last_name']
            return True

    def get_user_photo(self, user_id):

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
            top_photo[photo['id']] = photo['likes']['count']
        inverse = [(meaning, social) for social, meaning in top_photo.items()]
        sorted_top_photos = sorted(inverse, reverse=True)
        top = sorted_top_photos[0:3]
        people_photo_url.clear()
        for photos in top:
            people_photo_url.append(photos[1])

    def message_send_attach(self, user_id, owner_id, media_id):

        message_send_attach_url = self.url + 'messages.send'
        message_send_attach_params = {
            'user_id': user_id,
            'random_id': randrange(10 ** 7),
            'attachment': f'photo{owner_id}_{media_id}'
        }
        requests.get(message_send_attach_url, params={**self.params, **message_send_attach_params})


bot_vk = Bot(vk_token, '5.126')


def write_msg(user_id, message):

    vk.method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


def write_msg_attach(user_id, message):

    vk.method('messages.send', {'user_id': user_id, 'attachment': message, 'random_id': randrange(10 ** 7)})


def checking_exciting_table_bd_user_search(user_id):

    exists_users = []
    info = connection.execute("""SELECT * FROM user_search;""").fetchall()
    for user_ids in info:
        exists_users.append(user_ids[1])
    if user_id in exists_users:
        write_msg(searching_params['user_id_answer'], f'Отлично, '
                                                      f'я могу предложить два варианта поиска:\n'
                                                      f'если интересует быстрый поиск просто введи '
                                                      f'- быстрый поиск '
                                                      f'и в ответ я пришлю тебе ссылку на аккаунт '
                                                      f'и топ 3 фото профиля\n'
                                                      f'если же интересует детальный поиск просто введи '
                                                      f'и в ответ я пришлю тебе ссылку на аккаунт '
                                                      f'и топ 3 фото профиля')
    else:
        write_msg(searching_params['user_id_answer'], f'Отлично, '
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
        return True


def fast_searching_not_exists():

    check_list_not_exists = checking_exciting_in_table_vk_user_fast_search(searching_params['user_id'])
    while bot_vk.user_search_optimal_settings(main_info['city_id'], main_info['sex'], main_info['age_from'],
                                              main_info['age_to']) is False:
        print('---------------')
        print('продолжаем поиск')
        print('---------------')
    people_ids_not_exist_in_bd = result['user_result']
    print(people_ids_not_exist_in_bd)
    if people_ids_not_exist_in_bd not in check_list_not_exists:
        if bot_vk.user_closed_open(people_ids_not_exist_in_bd) is False:
            bot_vk.get_user_photo(people_ids_not_exist_in_bd)
            for each_photo in people_photo_url:
                photo_attach = f'photo{people_ids_not_exist_in_bd}_{each_photo}'
                write_msg_attach(searching_params['user_id_answer'], photo_attach)
            write_msg(searching_params['user_id_answer'], f'https://vk.com/id{people_ids_not_exist_in_bd}')
        elif bot_vk.user_closed_open(people_ids_not_exist_in_bd) is True:
            write_msg(searching_params['user_id_answer'], f'vk.com/id{people_ids_not_exist_in_bd}, '
                                                          f'к сожелению это закрытый профиль '
                                                          f'и я не могу отправить тебе его или ее фото.')
        people_found_info['user_id'] = people_ids_not_exist_in_bd
        add_info_in_vk_user_fast_search(people_ids_not_exist_in_bd)
        write_msg(event.user_id, 'Если хочешь просмотреть следующий результат просто введи еще.\n'
                                 'Если хочешь добавить пользователя в избранные введи добавить.\n'
                                 'Если хочешь вернуться к началу просто введи начало.')
        return True
    else:
        return False


def detail_searching_not_exists():

    check_list_not_exists = checking_exciting_in_table_vk_user_detail_search(searching_params['user_id'])
    while bot_vk.user_search_you_setting(searching_params['city_id'],
                                         searching_params['sex'],
                                         searching_params['age_from'],
                                         searching_params['age_to']) is False:
        print('---------------')
        print('продолжаем поиск')
        print('---------------')
    people_ids_not_exist_in_bd = result['user_result']
    if people_ids_not_exist_in_bd not in check_list_not_exists:
        if bot_vk.user_closed_open(people_ids_not_exist_in_bd) is False:
            bot_vk.get_user_photo(people_ids_not_exist_in_bd)
            for each_photo in people_photo_url:
                photo_attach = f'photo{people_ids_not_exist_in_bd}_{each_photo}'
                write_msg_attach(searching_params['user_id_answer'], photo_attach)
            write_msg(searching_params['user_id_answer'], f'https://vk.com/id{people_ids_not_exist_in_bd}')
        elif bot_vk.user_closed_open(people_ids_not_exist_in_bd) is True:
            write_msg(searching_params['user_id_answer'], f'vk.com/id{people_ids_not_exist_in_bd}, '
                                                          f'к сожелению это закрытый профиль '
                                                          f'и я не могу отправить тебе его или ее фото.')
        people_found_info['user_id'] = people_ids_not_exist_in_bd
        add_info_in_vk_user_detail_search(people_ids_not_exist_in_bd)
        write_msg(event.user_id, 'Если хочешь просмотреть следующий результат просто введи еще.\n'
                                 'Если хочешь добавить пользователя в избранные введи добавить.\n'
                                 'Если хочешь вернуться к началу просто введи начало.')
        return True
    else:
        return False


def add_info_to_favorite(user_id):

    connection.execute(
        f"""INSERT INTO favorites (user_id_added, user_search_id) VALUES ('{user_id}', '{searching_params['user_id']}');""")


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

    connection.execute(
        f"""INSERT INTO vk_user_fast_search (user_first_name, user_second_name, user_id, user_url, user_search_id) VALUES ('{people_found_info['first_name']}', '{people_found_info['last_name']}', '{user_id}', 'https://vk.com/id{user_id}', '{searching_params['user_id']}');""")


def add_info_in_vk_user_detail_search(user_id):

    connection.execute(
        f"""INSERT INTO vk_user_detail_search (user_first_name, user_second_name, user_id, user_url, user_search_id) VALUES ('{people_found_info['first_name']}', '{people_found_info['last_name']}', '{user_id}', 'https://vk.com/id{user_id}', '{searching_params['user_id']}');""")


def listen():
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                return event.text


def listen_for_sex():
    answer = listen()
    if answer == 'Мужского' or answer == 'мужского':
        searching_params['sex'] = 2
        write_msg(event.user_id, f'Отлично, тепрерь перейдем к городу, в каком городе ты хочешь найти людей?')
        return True
    elif answer == 'Женского' or answer == 'женского':
        searching_params['sex'] = 1
        write_msg(event.user_id, f'Отлично, тепрерь перейдем к городу, в каком городе ты хочешь найти людей?')
        return True
    elif answer == 'Не имеет значения' or answer == 'не имеет значения':
        searching_params['sex'] = 0
        write_msg(event.user_id, f'Отлично, тепрерь перейдем к городу, в каком городе ты хочешь найти людей?')
        return True
    else:
        write_msg(event.user_id, f'Не понял, введите пол человека для того чтобы я Вам мог подобрать людей?')
        return False


def listen_for_city():
    answer = listen()
    searching_params['city_name'] = answer
    searching_params['city_id'] = bot_vk.get_cities_id(answer)
    if searching_params['city_id'] is None:
        write_msg(event.user_id, f'Не знаю такого города')
        return False
    else:
        write_msg(event.user_id, f'{answer}, красивый город, '
                                 f'осталось лишь определиться с возрастным диапозоном поиска.\n'
                                 f'Для начала укажи минимальны возраст '
                                 f'с которого надо начать поиск.')
        return True


def listen_for_age_from():
    answer = listen()
    searching_params['age_from'] = answer
    return write_msg(event.user_id, f'ну и на полследок укажи максимальный возраст.')


def listen_for_age_to():
    answer = listen()
    searching_params['age_to'] = answer
    return write_msg(event.user_id, f'Олично начинаем поиск.')


def favorites_list(user_id):

    favorite_list = []
    info = connection.execute(f"""SELECT * FROM favorites WHERE user_search_id = {user_id};""").fetchall()
    for user_ids in info:
        favorite_list.append(user_ids[1])
    return favorite_list


def listen_for_command():
    write_msg(event.user_id, f'Если ранее ты уже добавлял людей в список избранных введи '
                             f'- избранные и я отправлю тебе список избранных.\n'
                             f'Или просто введи - поиск и приступим к поиску людей.')
    answer = listen()
    if answer == 'избранные':
        your_favorite = favorites_list(searching_params['user_id'])
        for every_id in your_favorite:
            write_msg(event.user_id, f'https://vk.com/id{every_id}')
        return True
    elif answer == 'поиск':
        return False


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
                                         f'а если ты хочешь найти для друга введи - для друга\n')
            elif request == 'для себя':
                searching_params['user_id_answer'] = event.user_id
                searching_params['user_id'] = event.user_id
                answer = listen_for_command()
                if answer is True:
                    write_msg(event.user_id, f'если ты хочешь найти для себя просто напиши - для себя,\n '
                                             f'а если ты хочешь найти для друга введи - для друга\n')
                elif answer is False:
                    checking_exciting_table_bd_user_search(searching_params['user_id'])
            elif request == 'для друга':
                write_msg(event.user_id, f'Отлично просто напиши мне id его аккаунта.')
                request = listen()
                searching_params['user_id_answer'] = event.user_id
                searching_params['user_id'] = int(request)
                answer = listen_for_command()
                if answer is True:
                    write_msg(event.user_id, f'если ты хочешь найти для себя просто напиши - для себя,\n '
                                             f'а если ты хочешь найти для друга введи - для друга\n')
                elif answer is False:
                    checking_exciting_table_bd_user_search(searching_params['user_id'])
            elif request == 'быстрый поиск':
                bot_vk.user_main_info(searching_params['user_id'])
                bot_vk.get_user_age(searching_params['user_id'])
                answer_for_exists = fast_searching_exists(searching_params['user_id'])
                if answer_for_exists is False:
                    write_msg(event.user_id, 'Часть информации отсутствует, рекомендую использовать детальный поиск.')
                elif answer_for_exists is True:
                    while fast_searching_not_exists() is False:
                        pass
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
                                    while fast_searching_not_exists() is False:
                                        pass
                                elif request == 'добавить':
                                    add_info_to_favorite(people_found_info['user_id'])
                                    write_msg(event.user_id,
                                              'Если хочешь просмотреть следующий результат просто введи еще.\n'
                                              'Если хочешь вернуться к началу просто введи начало.')
                                else:
                                    write_msg(event.user_id, f'Не знаю такой комманды')
            elif request == 'детальный поиск':
                write_msg(event.user_id, f'Отлично, давай тогда определися с несколькими параметрами.\n'
                                         f'Для начала давай определимся какого пола ты хочешь найти людей.\n'
                                         f'Мужского\n'
                                         f'Женского\n'
                                         f'Не имеет значения')
                while listen_for_sex() is False:
                    pass
                while listen_for_city() is False:
                    pass
                listen_for_age_from()
                listen_for_age_to()
                while detail_searching_not_exists() is False:
                    pass
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
                                while detail_searching_not_exists() is False:
                                    pass
                            elif request == 'добавить':
                                add_info_to_favorite(people_found_info['user_id'])
                                write_msg(event.user_id,
                                          'Если хочешь просмотреть следующий результат просто введи еще.\n'
                                          'Если хочешь вернуться к началу просто введи начало.')
                            else:
                                write_msg(event.user_id, f'Не знаю такой комманды')
            else:
                write_msg(event.user_id, 'не понял, потоврите запрос.')
