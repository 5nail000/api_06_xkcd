import os
import random
import requests

from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse


def send_request(url, params=None, files=None):
    if files:
        response = requests.post(url, params=params, files=files)    
    else:
        response = requests.get(url, params=params)
    response.raise_for_status()
    return response


def download_file(link, file_name, params=None):

    response = send_request(link, params=params)
    with open(Path.cwd()/file_name, 'wb') as file:
        file.write(response.content)
        return True


def get_xkcd(num):

    xkcd_response = send_request(f'https://xkcd.com/{num}/info.0.json')
    decoded_response = xkcd_response.json()
    xkcd_img_url = decoded_response['img']
    xkcd_img_name = os.path.basename(urlparse(xkcd_img_url).path)
    xkcd_alt = decoded_response['alt']

    return xkcd_img_name, xkcd_img_url, xkcd_alt


def get_wall_upload_server_vk(access_token, wall_id):
    method = 'photos.getWallUploadServer'
    url = f'https://api.vk.com/method/{method}'
    params = {
        'access_token': access_token,
        'v': 5.131,
        'group_id': wall_id
    }

    response = send_request(url, params=params)

    return response.json()['response']['upload_url']


def upload_image_vk(upload_url, img_file):
    files = {"photo": open(img_file, "rb")}

    upload_response = send_request(upload_url, files=files)
    decoded_response = upload_response.json()

    return decoded_response['server'], decoded_response['photo'], decoded_response['hash']


def save_wall_photo_vk(access_token, wall_id, server, photo, hash):
    method = 'photos.saveWallPhoto'
    url = f'https://api.vk.com/method/{method}'
    params = {
        'access_token': access_token,
        'v': 5.131,
        'group_id': wall_id,
        'server': server,
        'photo': photo,
        'hash': hash
    }

    saveWall_response = send_request(url, params=params)

    owner_id = saveWall_response.json()['response'][0]['owner_id']
    post_id = saveWall_response.json()['response'][0]['id']

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

    wallPost = send_request(url, params=params)

    return wallPost.json()


if __name__ == '__main__':

    load_dotenv()
    wall_id = int(os.environ['WALL_ID'])
    access_token = os.environ['ACCESS_TOKEN']
    folder = 'files'

    os.makedirs(folder, exist_ok=True)

    xkcd_filename, xkcd_url, xkcd_alt = get_xkcd(random.randint(1, 2723))
    download_file(xkcd_url, f'{folder}/{xkcd_filename}')

    vk_wall_upload_url = get_wall_upload_server_vk(access_token, wall_id)
    server, photo, hash = upload_image_vk(vk_wall_upload_url, f'{folder}/{xkcd_filename}')
    owner_id, post_id = save_wall_photo_vk(access_token, wall_id, server, photo, hash)
    wall_post = post_wall_vk(access_token, wall_id, owner_id, post_id, text=xkcd_alt)

    os.remove(f'{folder}/{xkcd_filename}')
