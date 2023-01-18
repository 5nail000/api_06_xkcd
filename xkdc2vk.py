import os
import random
import pprint
import logging
import requests

from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse


def download_file(link, file_name, params=None):

    response = requests.get(link, params=params)
    response.raise_for_status()

    with open(Path.cwd()/file_name, 'wb') as file:
        file.write(response.content)


def get_xkcd(num):

    xkcd_response = requests.get(f'https://xkcd.com/{num}/info.0.json')
    xkcd_response.raise_for_status()
    decoded_response = xkcd_response.json()

    xkcd_img_url = decoded_response['img']
    xkcd_img_name = os.path.basename(urlparse(xkcd_img_url).path)
    xkcd_alt = decoded_response['alt']

    return xkcd_img_name, xkcd_img_url, xkcd_alt


def check_error_response_vk(point_name, decoded_response):
    pp = pprint.PrettyPrinter(indent=3)
    if 'error' in decoded_response:
        log = (f'Error at point: {point_name}\n')
        log += (f'Data: {pp.pformat(decoded_response)}')

        logging.basicConfig(level=logging.ERROR,
                            filename="error.log",
                            filemode="w",
                            format="%(asctime)s - %(message)s",
                            datefmt='%Y.%m.%d  %H:%M:%S'
                            )
        logging.error(log)
        quit()


def get_wall_upload_server_vk(access_token, wall_id):
    method = 'photos.getWallUploadServer'
    url = f'https://api.vk.com/method/{method}'
    params = {
        'access_token': access_token,
        'v': 5.131,
        'group_id': wall_id
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
    decoded_response = response.json()
    check_error_response_vk('get_wall_upload_server_vk', decoded_response)

    return decoded_response['response']['upload_url']


def upload_image_vk(upload_url, img_file):

    with open(img_file, "rb") as file:
        files = {"photo": file}
        upload_response = requests.post(upload_url, files=files)

    upload_response.raise_for_status()
    decoded_response = upload_response.json()
    check_error_response_vk('upload_image_vk', decoded_response)

    return decoded_response['server'], decoded_response['photo'], decoded_response['hash']


def save_wall_photo_vk(access_token, wall_id, server, photo, upload_hash):
    method = 'photos.saveWallPhoto'
    url = f'https://api.vk.com/method/{method}'
    params = {
        'access_token': access_token,
        'v': 5.131,
        'group_id': wall_id,
        'server': server,
        'photo': photo,
        'hash': upload_hash
    }

    save_wall_response = requests.post(url, params=params)
    decoded_response = save_wall_response.json()
    check_error_response_vk('save_wall_photo_vk', decoded_response)

    owner_id = decoded_response['response'][0]['owner_id']
    post_id = decoded_response['response'][0]['id']

    return owner_id, post_id


def post_wall_vk(access_token, wall_id, owner_id, post_id, text=None):
    method = 'wall.post'
    url = f'https://api.vk.com/method/{method}'
    params = {
        'access_token': access_token,
        'v': 5.131,
        'owner_id': -wall_id,
        'from_group': 1,
        'attachments': f'photo{owner_id}_{post_id}',
        'message': text
    }

    wall_post_response = requests.post(url, params=params)
    decoded_response = wall_post_response.json()

    check_error_response_vk('post_wall_vk', decoded_response)

    return wall_post_request.json()


if __name__ == '__main__':

    load_dotenv()
    wall_id = int(os.environ['VK_WALL_ID'])
    access_token = os.environ['VK_ACCESS_TOKEN']

    folder = 'files'
    comics_total = 2723

    os.makedirs(folder, exist_ok=True)

    xkcd_filename, xkcd_url, xkcd_alt = get_xkcd(random.randint(1, comics_total))
    temp_file = Path.cwd()/folder/xkcd_filename
    download_file(xkcd_url, temp_file)

    try:
        vk_wall_upload_url = get_wall_upload_server_vk(access_token, wall_id)
        server, photo, upload_hash = upload_image_vk(vk_wall_upload_url, temp_file)
        owner_id, post_id = save_wall_photo_vk(access_token, wall_id, server, photo, upload_hash)
        wall_post_request = post_wall_vk(access_token, wall_id, owner_id, post_id, text=xkcd_alt)

    finally:
        os.remove(temp_file)
