#


import requests
from pprint import pprint


class YandexDisk:

    def __init__(self, token):
        self.token = token

    def get_files_list(self):
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources/files'
        headers = self.get_headers()
        response = requests.get(files_url, headers=headers)
        return response.json()

    def makedir(self, dir_path: str):
        files_url = 'https://cloud-api.yandex.net/v1/disk/resources'
        headers = self.get_headers()
        params = {'path': dir_path.strip()}
        response = requests.put(files_url, headers=headers, params=params)
        return response.json()

    def get_headers(self):
        return {'Content-Type': 'application/json',
                'Authorization': 'OAuth {}'.format(self.token)}

    def _get_upload_link(self, ya_disk_file_path: str):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': ya_disk_file_path, 'overwrite': 'true'}
        response = requests.get(upload_url, headers=headers, params=params)
        # pprint(response.json())  # ---------------------------------------------
        return response.json()

    def upload_file_to_disk(self, upload_path: str, saved_file_name: str):
        response_link = self._get_upload_link(ya_disk_file_path=upload_path)
        href = response_link.get('href', '')
        # print('ya_disk_file_path:', upload_path, 'filename:', saved_file_name)  # -------------------------

        temp_upload_file_name = 'foto'

        temp_upload_file_name += '.tmp'
        response = requests.get(saved_file_name, stream=True)
        with open(temp_upload_file_name, 'wb') as temp:
            for buf in response.iter_content():
                if buf:
                    temp.write(buf)
        with open(temp_upload_file_name, 'rb') as foto:
            response = requests.put(href, data=foto)
            response.raise_for_status()

    def upload2_file_to_disk(self, ya_path: str, vk_url: str):
        upload_url = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        headers = self.get_headers()
        params = {'path': ya_path, 'url': vk_url}
        response = requests.post(upload_url, headers=headers, params=params)
