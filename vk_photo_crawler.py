#
import json
from pprint import pprint
import requests


def print_response_err(response: dict, count: int) -> dict:
    err = {} if count else response.get('error', {})
    if err:
        print(f'\t{err.get("error_msg", "")} (err{err.get("error_code", "")})')  # ------------------------------
    return err


def get_title_user(user: dict):
    return f"id-{str(user['id'])}_{user['first_name']}{'_' + user['last_name'] if user['last_name'] else ''}"


class VkUserPhotoCrawler:
    def __init__(self, token: str, api_ver: str = '5.131'):
        self._VK_TOKEN = token
        self._API_VK_VER = api_ver
        self.max_count_photos = 0
        print(f"Создан объект фото-граббера!")

    def get_users(self, vk_ids: str, name_case='nom', fields="photo_id"):
        """ Получаем пользователя """
        url = 'https://api.vk.com/method/users.get'
        params = {'user_ids': vk_ids,
                  'fields': fields,
                  'name_case': name_case,
                  'access_token': self._VK_TOKEN,
                  'v': self._API_VK_VER}
        res = requests.get(url, params=params).json()
        # pprint(res)  # ----------------------------------
        response = res.get('response', {})
        print_response_err(res, len(response))
        return response

    def get_user_photo_albums(self, user: dict, user_title: str = ''):
        """
        Поиск альбомов пользователя методом photos.get и сервис-токеном.
        Фото берется сначала из данных, полученных из vk_api методом user.get.
        Затем ищутся фото в профиле пользователя методом photos.get.
        :param user: инфо о пользователе VK
        :param user_title: описание пользователя VK
        :return: albums_count, albums: количество альбомов и их список
        """
        vk_user_id = str(user['id'])
        if not user_title:
            user_title = 'с ' + get_title_user(user)
        print(f"\nАльбомы пользователя {user_title}:")  # ----------------------------

        url = 'https://api.vk.com/method/photos.getAlbums'
        params = {'owner_id': vk_user_id,
                  'access_token': self._VK_TOKEN,
                  'v': self._API_VK_VER}
        albums = []
        while True:
            params['offset'] = len(albums)
            res = requests.get(url, params=params).json()
            # pprint(res)  # ----------------------------------
            response = res.get('response', {})
            albums_count: int = response.get('count', 0)
            print_response_err(res, albums_count)  # ---------------------------
            current_albums: list = response.get('items', [])
            print(f'\tНайдено доступных альбомов: {len(current_albums)} из {albums_count}')  # --------------
            albums += current_albums
            if len(albums) == albums_count:
                break
        albums = list(album for album in albums if album['size'] > 0)
        return albums_count, albums

    def get_user_album_photos(self, vk_id: str = '1', album_id: str = 'profile', offset: int = 0):
        """
        Поиск фотографий пользователя методом photos.get и сервис-токеном.
        Фото берется сначала из данных, полученных из vk_api методом user.get.
        Затем ищутся фото в профиле пользователя методом photos.get.
        :param vk_id: id пользователя VK
        :param album_id: id альбома пользователя VK
        :param offset:
        :return: количество фото и их список взяты из альбома
        """
        url = 'https://api.vk.com/method/photos.get'
        params = {'owner_id': vk_id,
                  'album_id': album_id,  # служебные: 'profile', 'wall'
                  'extended': 1,
                  'offset': offset,
                  'access_token': self._VK_TOKEN,
                  'v': self._API_VK_VER}
        res = requests.get(url, params=params).json()
        # pprint(res)  # ----------------------------------
        response = res.get('response', {})

        album_photos_count: int = response.get('count', 0)
        print_response_err(res, album_photos_count)
        album_photos_current_block: list = response.get('items', [])
        current_photos_block_count: int = len(album_photos_current_block)
        print(f'\tНайдено фото: {current_photos_block_count} из {album_photos_count} в альбоме')  # --------------
        return album_photos_count, album_photos_current_block

    def pump_out_album(self, user: dict, album_id='profile', album_title='служебный'):
        """
        Выкачать фото из заданного альбома пользователя VK
        :param user: инофо пользователя
        :param album_id: vk id альбома
        :param album_title: заголовок альбома
        :return:album: list of photo dict: {'url': url,'likes': likes}
        """

        def get_max_size_photo(photo) -> dict:
            return max((size_photo for size_photo in photo['sizes']),
                       key=lambda size: size['height'] + size['width'], default=0)

        vk_user_id = str(user['id'])
        print(f"\nФото из альбома '{album_id}' ({album_title}) пользователя {get_title_user(user)}:")
        album = []
        while True:
            album_photos_count, album_photos = self.get_user_album_photos(vk_user_id, album_id, len(album))
            photos = list({'url': get_max_size_photo(photo)['url'],
                           'likes': photo['likes']['count'] if photo.get('likes', {}) else 0}
                          for photo in album_photos)
            album += photos
            if ((len(album) >= self.max_count_photos if self.max_count_photos else False)
                    or len(album) == album_photos_count):
                break
        album = list(url for num, url in enumerate(album)
                     if (num < self.max_count_photos if self.max_count_photos else True))  # ограничитель кол-ва фото
        return album

    def start(self, vk_ids: list, max_count_photos: int = 0, albums_string: str = ''):
        try:
            self.max_count_photos = int(max_count_photos)
        except ValueError as err:
            print(err)

        def write_json_file(dict_):
            filename = 'vk_photos.json'
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(dict_, f, ensure_ascii=False, indent=2)
                print(f'\nИнформация о найденных фото VK пользователей сохранена в файл {filename}')
            except OSError as other:
                print(f'There were problems opening the file {filename}: \n\t{other}')
                print('Sorry, the results are not saved to a json file...')
                filename = ''
            return filename

        def print_users(users: list):
            if len(users):
                print('\tСписок пользователей для фото-парсинга:\n\t' +
                      '\n\t'.join(
                          f"{num + 1}.\t{get_title_user(user)}"
                          for num, user in enumerate(users)))

        def print_albums(albums: list):
            # albums = list(album for album in albums if album['size'] > 0)
            if len(albums):
                print('\tСписок всех найденных непустых доступных альбомов пользователя:\n\t' +
                      '\n\t'.join(
                          f"{num + 1}.\t({album['id']})\t{album['title']} ({album['size']} фото)"
                          for num, album in enumerate(albums)))

        def print_album(photos: list, divider: int = 2, name_splitter='&'):

            def shortened_url(url: str) -> str:
                path = url.split('/')
                shortened_path = path[:-1] if len(path) < 5 else path[:int(len(path) / divider)]
                shortened_path = '/'.join(shortened_path) + f'/{".../" if divider > 1 else ""}'
                if name_splitter not in ['?', '&']:
                    shortened_filename = path[-1]
                else:
                    filename = path[-1].split(name_splitter)
                    shortened_filename = f'{filename[0]}{(name_splitter + "...") if len(filename) > 1 else ""}'
                return shortened_path + shortened_filename

            if len(photos):
                print(
                    (f'\tСписок найденных фото в альбоме, максимум {self.max_count_photos}' if self.max_count_photos
                     else '\tСписок всех найденных фото в альбоме') +
                    ':\n\t' + '\n\t'.join(
                        f'{num + 1}. {shortened_url(photo["url"])}, {photo["likes"]} likes'
                        for num, photo in enumerate(photos)
                        if (num < self.max_count_photos if self.max_count_photos else True)
                    ))

        users_: list = self.get_users(','.join(vk_ids))
        print_users(users_)

        selected_album_ids = list(album_.strip() for album_ in albums_string.split(',') if album_.strip())
        print('\nСмотреть', f'альбомы: {selected_album_ids}' if len(selected_album_ids) else 'все альбомы')

        service_album_ids = ['profile', 'wall']

        users_albums = []  # нужные альбомы нужных пользователей

        for user_ in users_:
            albums_count_, albums_ = self.get_user_photo_albums(user_)
            print_albums(albums_)  # ----------------------------
            album_ids = service_album_ids + list(album_['id'] for album_ in albums_)

            real_albums = []  # собираем из альбомов, которые есть в найденных у пользователя

            if albums_string:  # если заданы конкретные альбомы
                for album_id in selected_album_ids:
                    if album_id not in album_ids:  # несуществующий альбом
                        continue
                    if album_id in service_album_ids:  # служебный альбом
                        photos_ = self.pump_out_album(user_, album_id)
                        print_album(photos_)
                        real_albums.append({'album_id': album_id,
                                            'album_title': 'служебный',
                                            'count': len(photos_),
                                            'photos': photos_})
                        continue
                    for album_ in albums_:
                        if album_['id'] == album_id:  # есть в остальных альбомах пользователя
                            photos_ = self.pump_out_album(user_, album_id)
                            print_album(photos_)
                            real_albums.append({'album_id': album_id,
                                                'album_title': album_['title'],
                                                'count': len(photos_),
                                                'photos': photos_})
                            continue
            else:  # если работаем по всем альбомам пользователя
                for album_id in service_album_ids:  # добавляем служебные альбомы profile, wall:
                    photos_ = self.pump_out_album(user_, album_id)
                    print_album(photos_)
                    real_albums.append({'album_id': album_id,
                                        'album_title': 'служебный',
                                        'count': len(photos_),
                                        'photos': photos_})
                user_albums = list(  # добавляем все остальные найденные альбомы пользователя:
                    {'album_id': album['id'],
                     'album_title': album['title'],
                     'photos': self.pump_out_album(user_, album['id'])}
                    for album in albums_)
                for album in user_albums:
                    album['count'] = len(album['photos'])
                real_albums += user_albums

            # Собираем альбомы всех пользователей:
            users_albums.append({'user_id': user_['id'],
                                 'user_title': get_title_user(user_),
                                 'count': len(real_albums),
                                 'albums': real_albums})

        return write_json_file(users_albums)
