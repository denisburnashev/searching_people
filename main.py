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


class Bot:
    url = 'https://api.vk.com/method/'
    user_id_answer = {}
    main_info = {}
    people_found_info = {}
    result = {}
    people_ids = []
    people_photo_url = []
    searching_params = {}

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
        self.main_info['first_name'] = info['first_name']
        self.main_info['last_name'] = info['last_name']
        if info.get('sex') is None:
            self.main_info['sex'] = None
        else:
            if info['sex'] == 2:
                self.main_info['sex'] = 1
            elif info['sex'] == 1:
                self.main_info['sex'] = 2
            else:
                self.main_info['sex'] = 0
        if info.get('city') is None:
            self.main_info['city_id'] = None
        else:
            self.main_info['city_id'] = info['city']['id']
        print(self.main_info)

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
            self.main_info['age_from'] = None
            self.main_info['age_to'] = None
        else:
            your_bdate = info['bdate']
            edit_your_bdate = your_bdate.replace('.', ' ')
            your_year = edit_your_bdate.split()[2]
            today_year = str(date.today())
            today_year = today_year[:4]
            your_age = int(today_year) - int(your_year)
            self.main_info['age_from'] = your_age - 2
            self.main_info['age_to'] = your_age + 2

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
        self.searching_params['offset'] = random_people

        user_search_optimal_settings_url = self.url + 'users.search'
        user_search_optimal_settings_params = {
            'offset': self.searching_params['offset'],
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
            self.result['user_result'] = user_info[0]['id']
            self.people_found_info['first_name'] = user_info[0]['first_name']
            self.people_found_info['last_name'] = user_info[0]['last_name']
            return True

    def user_search_you_setting(self, city_id, sex, age_from, age_to):
        random_people = randrange(1, 1000)
        self.searching_params['offset'] = random_people

        user_search_you_setting_url = self.url + 'users.search'
        user_search_you_setting_params = {
            'offset': self.searching_params['offset'],
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
            self.result['user_result'] = user_info[0]['id']
            self.people_found_info['first_name'] = user_info[0]['first_name']
            self.people_found_info['last_name'] = user_info[0]['last_name']
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
        self.people_photo_url.clear()
        for photos in top:
            self.people_photo_url.append(photos[1])

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

    vk_bot_token().method('messages.send', {'user_id': user_id, 'message': message, 'random_id': randrange(10 ** 7)})


def write_msg_attach(user_id, message):

    vk_bot_token().method('messages.send', {'user_id': user_id, 'attachment': message, 'random_id': randrange(10 ** 7)})


def checking_exciting_table_bd_user_search(user_id):

    exists_users = []
    info = connection.execute("""SELECT * FROM user_search;""").fetchall()
    for user_ids in info:
        exists_users.append(user_ids[1])
    if user_id in exists_users:
        write_msg(bot_vk.user_id_answer['user_id_answer'], f'Отлично, '
                                                             f'я могу предложить два варианта поиска:\n'
                                                             f'если интересует быстрый поиск просто введи '
                                                             f'- быстрый поиск '
                                                             f'и в ответ я пришлю тебе ссылку на аккаунт '
                                                             f'и топ 3 фото профиля\n'
                                                             f'если же интересует детальный поиск просто введи '
                                                             f'и в ответ я пришлю тебе ссылку на аккаунт '
                                                             f'и топ 3 фото профиля')
    else:
        write_msg(bot_vk.user_id_answer['user_id_answer'], f'Отлично, '
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

    if bot_vk.main_info['sex'] is None or \
            bot_vk.main_info['city_id'] is None or \
            bot_vk.main_info['age_from'] is None or \
            bot_vk.main_info['age_to'] is None:
        return False
    else:
        return True


def fast_searching_not_exists():

    check_list_not_exists = checking_exciting_in_table_vk_user_fast_search(bot_vk.searching_params['user_id'])
    while bot_vk.user_search_optimal_settings(bot_vk.main_info['city_id'],
                                              bot_vk.main_info['sex'],
                                              bot_vk.main_info['age_from'],
                                              bot_vk.main_info['age_to']) is False:
        print('---------------')
        print('продолжаем поиск')
        print('---------------')
    people_ids_not_exist_in_bd = bot_vk.result['user_result']
    print(people_ids_not_exist_in_bd)
    if people_ids_not_exist_in_bd not in check_list_not_exists:
        if bot_vk.user_closed_open(people_ids_not_exist_in_bd) is False:
            bot_vk.get_user_photo(people_ids_not_exist_in_bd)
            for each_photo in bot_vk.people_photo_url:
                photo_attach = f'photo{people_ids_not_exist_in_bd}_{each_photo}'
                write_msg_attach(bot_vk.user_id_answer['user_id_answer'], photo_attach)
            write_msg(bot_vk.user_id_answer['user_id_answer'], f'https://vk.com/id{people_ids_not_exist_in_bd}')
        elif bot_vk.user_closed_open(people_ids_not_exist_in_bd) is True:
            write_msg(bot_vk.user_id_answer['user_id_answer'], f'vk.com/id{people_ids_not_exist_in_bd}, '
                                                                 f'к сожелению это закрытый профиль '
                                                                 f'и я не могу отправить тебе его или ее фото.')
        bot_vk.people_found_info['user_id'] = people_ids_not_exist_in_bd
        add_info_in_vk_user_fast_search(people_ids_not_exist_in_bd)
        write_msg(bot_vk.user_id_answer['user_id_answer'], 'Если хочешь просмотреть следующий результат '
                                                           'просто введи еще.\n'
                                                           'Если хочешь добавить пользователя '
                                                           'в избранные введи добавить.\n'
                                                           'Если хочешь вернуться к началу просто введи начало.')
        return True
    else:
        return False


def detail_searching_not_exists():

    check_list_not_exists = checking_exciting_in_table_vk_user_detail_search(bot_vk.searching_params['user_id'])
    while bot_vk.user_search_you_setting(bot_vk.searching_params['city_id'],
                                         bot_vk.searching_params['sex'],
                                         bot_vk.searching_params['age_from'],
                                         bot_vk.searching_params['age_to']) is False:
        print('---------------')
        print('продолжаем поиск')
        print('---------------')
    people_ids_not_exist_in_bd = bot_vk.result['user_result']
    if people_ids_not_exist_in_bd not in check_list_not_exists:
        if bot_vk.user_closed_open(people_ids_not_exist_in_bd) is False:
            bot_vk.get_user_photo(people_ids_not_exist_in_bd)
            for each_photo in bot_vk.people_photo_url:
                photo_attach = f'photo{people_ids_not_exist_in_bd}_{each_photo}'
                write_msg_attach(bot_vk.user_id_answer['user_id_answer'], photo_attach)
            write_msg(bot_vk.user_id_answer['user_id_answer'], f'https://vk.com/id{people_ids_not_exist_in_bd}')
        elif bot_vk.user_closed_open(people_ids_not_exist_in_bd) is True:
            write_msg(bot_vk.user_id_answer['user_id_answer'], f'vk.com/id{people_ids_not_exist_in_bd}, '
                                                                 f'к сожелению это закрытый профиль '
                                                                 f'и я не могу отправить тебе его или ее фото.')
        bot_vk.people_found_info['user_id'] = people_ids_not_exist_in_bd
        add_info_in_vk_user_detail_search(people_ids_not_exist_in_bd)
        write_msg(bot_vk.user_id_answer['user_id_answer'], 'Если хочешь просмотреть следующий '
                                                           'результат просто введи еще.\n'
                                                           'Если хочешь добавить пользователя '
                                                           'в избранные введи добавить.\n'
                                                           'Если хочешь вернуться к началу просто введи начало.')
        return True
    else:
        return False


def add_info_to_favorite(user_id):

    connection.execute(
        f"""INSERT INTO favorites (user_id_added, user_search_id) VALUES ('{user_id}', '{bot_vk.searching_params['user_id']}');""")


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
        f"""INSERT INTO vk_user_fast_search (user_first_name, user_second_name, user_id, user_url, user_search_id) VALUES ('{bot_vk.people_found_info['first_name']}', '{bot_vk.people_found_info['last_name']}', '{user_id}', 'https://vk.com/id{user_id}', '{bot_vk.searching_params['user_id']}');""")


def add_info_in_vk_user_detail_search(user_id):

    connection.execute(
        f"""INSERT INTO vk_user_detail_search (user_first_name, user_second_name, user_id, user_url, user_search_id) VALUES ('{bot_vk.people_found_info['first_name']}', '{bot_vk.people_found_info['last_name']}', '{user_id}', 'https://vk.com/id{user_id}', '{bot_vk.searching_params['user_id']}');""")


def listen():
    for event in vk_bot_message().listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                bot_vk.user_id_answer['user_id_answer'] = event.user_id
                return event.text


def listen_for_sex():
    answer = listen()
    if answer == 'Мужского' or answer == 'мужского':
        bot_vk.searching_params['sex'] = 2
        write_msg(bot_vk.user_id_answer['user_id_answer'], f'Отлично, тепрерь перейдем к городу, '
                                                           f'в каком городе ты хочешь найти людей?')
        return True
    elif answer == 'Женского' or answer == 'женского':
        bot_vk.searching_params['sex'] = 1
        write_msg(bot_vk.user_id_answer['user_id_answer'], f'Отлично, тепрерь перейдем к городу, '
                                                           f'в каком городе ты хочешь найти людей?')
        return True
    elif answer == 'Не имеет значения' or answer == 'не имеет значения':
        bot_vk.searching_params['sex'] = 0
        write_msg(bot_vk.user_id_answer['user_id_answer'], f'Отлично, тепрерь перейдем к городу, '
                                                           f'в каком городе ты хочешь найти людей?')
        return True
    else:
        write_msg(bot_vk.user_id_answer['user_id_answer'], f'Не понял, введите пол человека '
                                                           f'для того чтобы я Вам мог подобрать людей?')
        return False


def listen_for_city():
    answer = listen()
    bot_vk.searching_params['city_name'] = answer
    bot_vk.searching_params['city_id'] = bot_vk.get_cities_id(answer)
    if bot_vk.searching_params['city_id'] is None:
        write_msg(bot_vk.user_id_answer['user_id_answer'], f'Не знаю такого города')
        return False
    else:
        write_msg(bot_vk.user_id_answer['user_id_answer'], f'{answer}, красивый город, '
                                                           f'осталось лишь определиться с '
                                                           f'возрастным диапозоном поиска.\n'
                                                           f'Для начала укажи минимальны возраст '
                                                           f'с которого надо начать поиск.')
        return True


def listen_for_age_from():
    answer = listen()
    bot_vk.searching_params['age_from'] = answer
    return write_msg(bot_vk.user_id_answer['user_id_answer'], f'ну и на полследок укажи максимальный возраст.')


def listen_for_age_to():
    answer = listen()
    bot_vk.searching_params['age_to'] = answer
    return write_msg(bot_vk.user_id_answer['user_id_answer'], f'Олично начинаем поиск.')


def favorites_list(user_id):

    favorite_list = []
    info = connection.execute(f"""SELECT * FROM favorites WHERE user_search_id = {user_id};""").fetchall()
    for user_ids in info:
        favorite_list.append(user_ids[1])
    return favorite_list


def listen_for_command():
    write_msg(bot_vk.user_id_answer['user_id_answer'], f'Если ранее ты уже добавлял людей в список избранных введи '
                                                       f'- избранные и я отправлю тебе список избранных.\n'
                                                       f'Или просто введи - поиск и приступим к поиску людей.')
    answer = listen()
    if answer == 'избранные':
        your_favorite = favorites_list(bot_vk.searching_params['user_id'])
        for every_id in your_favorite:
            write_msg(bot_vk.user_id_answer['user_id_answer'], f'https://vk.com/id{every_id}')
        return True
    elif answer == 'поиск':
        return False


def vk_bot_token():
    vk = vk_api.VkApi(token=group_token)
    return vk


def vk_bot_message():
    longpoll = VkLongPoll(vk_bot_token())
    return longpoll


def main():
    while True:
        request = listen()
        if request == 'Привет' or request == 'привет' or request == 'Хай' or request == 'хай':
            write_msg(bot_vk.user_id_answer['user_id_answer'], f'Привет это бот - vkinder по поиску людей.\n'
                                                               f'Для кого ты хочешь найти подходящих людей?\n'
                                                               f'если ты хочешь найти для себя '
                                                               f'просто напиши - для себя,\n '
                                                               f'а если ты хочешь найти для друга '
                                                               f'введи - для друга\n')
        elif request == 'для себя':
            bot_vk.searching_params['user_id_answer'] = bot_vk.user_id_answer['user_id_answer']
            bot_vk.searching_params['user_id'] = bot_vk.user_id_answer['user_id_answer']
            answer = listen_for_command()
            if answer is True:
                write_msg(bot_vk.user_id_answer['user_id_answer'], f'если ты хочешь найти для себя '
                                                                   f'просто напиши - для себя,\n '
                                                                   f'а если ты хочешь найти для друга '
                                                                   f'введи - для друга\n')
            elif answer is False:
                checking_exciting_table_bd_user_search(bot_vk.searching_params['user_id'])
        elif request == 'для друга':
            write_msg(bot_vk.user_id_answer['user_id_answer'], f'Отлично просто напиши мне id его аккаунта.')
            request = listen()
            bot_vk.searching_params['user_id_answer'] = bot_vk.user_id_answer['user_id_answer']
            bot_vk.searching_params['user_id'] = int(request)
            answer = listen_for_command()
            if answer is True:
                write_msg(bot_vk.user_id_answer['user_id_answer'], f'если ты хочешь найти для себя '
                                                                   f'просто напиши - для себя,\n '
                                                                   f'а если ты хочешь найти для друга '
                                                                   f'введи - для друга\n')
            elif answer is False:
                checking_exciting_table_bd_user_search(bot_vk.searching_params['user_id'])
        elif request == 'быстрый поиск':
            bot_vk.user_main_info(bot_vk.searching_params['user_id'])
            bot_vk.get_user_age(bot_vk.searching_params['user_id'])
            answer_for_exists = fast_searching_exists(bot_vk.searching_params['user_id'])
            if answer_for_exists is False:
                write_msg(bot_vk.user_id_answer['user_id_answer'], 'Часть информации отсутствует, '
                                                                   'рекомендую использовать детальный поиск.')
            elif answer_for_exists is True:
                while fast_searching_not_exists() is False:
                    pass
                for event in vk_bot_message().listen():
                    if event.type == VkEventType.MESSAGE_NEW:
                        if event.to_me:
                            request = event.text
                            if request == 'начало':
                                write_msg(event.user_id, f'Привет это бот - vkinder по поиску людей.\n'
                                                         f'Для кого ты хочешь найти подходящих людей?\n'
                                                         f'если ты хочешь найти для себя '
                                                         f'просто напиши - для себя,\n '
                                                         f'а если ты хочешь найти для друга '
                                                         f'напиши - для друга')
                                break
                            elif request == 'еще':
                                while fast_searching_not_exists() is False:
                                    pass
                            elif request == 'добавить':
                                add_info_to_favorite(bot_vk.people_found_info['user_id'])
                                write_msg(bot_vk.user_id_answer['user_id_answer'],
                                          'Если хочешь просмотреть следующий результат просто введи еще.\n'
                                          'Если хочешь вернуться к началу просто введи начало.')
                            else:
                                write_msg(bot_vk.user_id_answer['user_id_answer'], f'Не знаю такой комманды')
        elif request == 'детальный поиск':
            write_msg(bot_vk.user_id_answer['user_id_answer'], f'Отлично, давай тогда определися '
                                                               f'с несколькими параметрами.\n'
                                                               f'Для начала давай определимся какого пола '
                                                               f'ты хочешь найти людей.\n'
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
            for event in vk_bot_message().listen():
                if event.type == VkEventType.MESSAGE_NEW:
                    if event.to_me:
                        request = event.text
                        if request == 'начало':
                            write_msg(bot_vk.user_id_answer['user_id_answer'], f'Привет это бот - vkinder '
                                                                               f'по поиску людей.\n'
                                                                               f'Для кого ты хочешь найти '
                                                                               f'подходящих людей?\n'
                                                                               f'если ты хочешь найти для себя '
                                                                               f'просто напиши - для себя,\n '
                                                                               f'а если ты хочешь найти для друга '
                                                                               f'введи - для друга')
                            break
                        elif request == 'еще':
                            while detail_searching_not_exists() is False:
                                pass
                        elif request == 'добавить':
                            add_info_to_favorite(bot_vk.people_found_info['user_id'])
                            write_msg(bot_vk.user_id_answer['user_id_answer'],
                                      'Если хочешь просмотреть следующий результат просто введи еще.\n'
                                      'Если хочешь вернуться к началу просто введи начало.')
                        else:
                            write_msg(bot_vk.user_id_answer['user_id_answer'], f'Не знаю такой комманды')
        else:
            write_msg(bot_vk.user_id_answer['user_id_answer'], 'не понял, потоврите запрос.')


main()
