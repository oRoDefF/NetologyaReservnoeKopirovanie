import configparser


class Token:
    config = configparser.ConfigParser()

    try:
        config.read('settings.ini')
        VK = config['VKontakte']['vk_token']
        VK_VERSION = config['VKontakte']['vk_version']
        YA = config['Yandex']['ya_token']
        YA_PATH = config['Yandex']['ya_path']

    except Exception as err:
        print('Отсутствует токен', err)
        VK = ''
        YA = ''

    if not (VK and YA):
        config['DEFAULT'] = {
            'vk_token': '',
            'vk_version': '5.131',
            'ya_token': '',
            'ya_path': 'Test'
        }

        while not VK:
            VK = input('\nОтсутствует токен api VKontakte! Введите сервис-токен VK: ')
        VK_VERSION = config['DEFAULT']['vk_version']
        config['VKontakte'] = {'vk_token': VK, 'vk_version': VK_VERSION}

        while not YA:
            YA = input('\nОтсутствует токен api Yandex! Введите свой токен Yandex: ')
        YA_PATH = config['DEFAULT']['ya_path']
        config['Yandex'] = {'ya_token': YA, 'ya_path': YA_PATH}

        with open('settings.ini', 'w') as configfile:
            config.write(configfile)

