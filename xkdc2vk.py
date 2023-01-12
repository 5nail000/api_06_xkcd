import os
import random
import requests

from pathlib import Path
from dotenv import load_dotenv
from urllib.parse import urlparse


def send_request(url, params=None, post=None, files=None):
    if post:
        response = requests.post(url, params=params, files=files)
    else:
        response = requests.get(url, params=params)

    response.raise_for_status()
    return response


def download_file(link, file_name, folder='Files', params=None):

    response = send_request(link, params=params)
    os.makedirs(folder, exist_ok=True)
    with open(Path.cwd()/folder/file_name, 'wb') as file:
        file.write(response.content)
        return True


def get_xkcd(num):

    xkcd_response = send_request(f'https://xkcd.com/{num}/info.0.json')
    xkcd_img = xkcd_response.json()['img']
    xkcd_alt = xkcd_response.json()['alt']
    xkcd_img_name = os.path.basename(urlparse(xkcd_img).path)

    return xkcd_img_name, xkcd_img, xkcd_alt


def vk_getWallUploadServer(access_token, wall_id):
    method = 'photos.getWallUploadServer'
    url = f'https://api.vk.com/method/{method}'
    params = {
        'access_token': access_token,
        'v': 5.131,
        'group_id': wall_id
    }

    upload_Server = send_request(url, params=params, post=True)

    return upload_Server.json()['response']['upload_url']


def vk_uploadImage(upload_url, img_file):
    files = {"photo": open(img_file, "rb")}

    upload_response = send_request(upload_url, files=files, post=True)

    server = upload_response.json()['server']
    photo = upload_response.json()['photo']
    hash = upload_response.json()['hash']

    return server, photo, hash


def vk_saveWallPhoto(access_token, wall_id, server, photo, hash):
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

    saveWall_response = send_request(url, params=params, post=True)

    owner_id = saveWall_response.json()['response'][0]['owner_id']
    post_id = saveWall_response.json()['response'][0]['id']

    return owner_id, post_id


def vk_wallPost(access_token, wall_id, owner_id, post_id, text=None):
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

    wallPost = send_request(url, params=params, post=True)

    return wallPost.json()


if __name__ == '__main__':

    load_dotenv()
    wall_id = int(os.environ['WALL_ID'])
    access_token = os.environ['ACCESS_TOKEN']

    xkcd_filename, xkcd_url, xkcd_alt = get_xkcd(random.randint(1, 2723))
    download_file(xkcd_url, xkcd_filename, folder='files')

    vk_UploadServer = vk_getWallUploadServer(access_token, wall_id)
    server, photo, hash = vk_uploadImage(vk_UploadServer, f'files/{xkcd_filename}')
    owner_id, post_id = vk_saveWallPhoto(access_token, wall_id, server, photo, hash)
    wallPost = vk_wallPost(access_token, wall_id, owner_id, post_id, text=xkcd_alt)

    os.remove(f'files/{xkcd_filename}')
