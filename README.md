# Курсовой проект «Резервное копирование» первого блока «Основы языка программирования Python»

> **PY-62** — общий курс Python: 
> *    модуль "Основы языка программирования Python"
> *    КУРСОВАЯ РАБОТА
> *    «Резервное копирование»
> *    [Задание на сайте **Нетологии**](https://github.com/netology-code/py-diplom-basic)

### Использование:

python foto_crawler.py [-h] [-vk VK_USER_IDS_STRING] [-ya YANDEX_DIR] [-m MAX_COUNT_PHOTOS] [-a ALBUMS_STRING] [-ver]

> This is VK photo crawler sample Py program
>
> **options:**
> - **-h, --help**            
> show this help message and exit
###### User id collection of VK users:
> - **-vk _VK_USER_IDS_STRING_, --vkIds _VK_USER_IDS_STRING_**
###### Yandex disk path to store photos:
> - **-ya _YANDEX_DIR_, --yandex _YANDEX_DIR_**
###### The maximum needed count of photos from each album of the VK user:
> - **-m _MAX_COUNT_PHOTOS_, --max _MAX_COUNT_PHOTOS_**
###### Album id collection of VK user:
> - **-a _VK_ALBUM_IDS_STRING_, --albums _VK_ALBUM_IDS_STRING_**
###### show program's version number and exit
> - -**ver, --version**

For example,

Фото пользователей VK c id = ['11', '14', '17'] из альбомов с id = ['profile', 'wall'] по 5 фото из каждого. Сохранить на Я.Диск в папку 'Test17':
> - python foto_crawler.py -vk 11,14,17 -ya Test17 -m 5 -a profile,wall

Фото пользователя VK c id = '17' по умолчанию из всех его доступных непустых альбомов по 2 фото из каждого. Сохранить на Я.Диск по умолчанию в папку 'Test':
> - python foto_crawler.py -vk 17 -m 2

Фото пользователей VK c id, введенных с клавиатуры, из альбома с id = 'profile', по умолчанию все фото альбома. Сохранить на Я.Диск по умолчанию в папку 'Test':
> - python foto_crawler.py -a profile

Все фото пользователей VK c id, введенных с клавиатуры, из всех доступных непустых альбомов каждого пользователя. Сохранить на Я.Диск в папку 'Test':
> - python foto_crawler.py
