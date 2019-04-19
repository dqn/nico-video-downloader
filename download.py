import sys
import os
import requests
import urllib.parse
from bs4 import BeautifulSoup

VIDEOS_DIR = './videos'
DELAY_SECOND = 5

def is_logined(session):
    url = 'http://www.nicovideo.jp/'
    return (session.get(url).headers['x-niconico-authflag'] == '1')

def login(session, mail, password):
    url = 'https://account.nicovideo.jp/api/v1/login'
    params = {
        'mail_tel': mail,
        'password': password,
    }
    session.post(url, params=params)

def get_thumb_info(session, video_id):
    url = 'http://ext.nicovideo.jp/api/getthumbinfo/{}'.format(video_id)
    return session.get(url)

def get_flv(session, video_id):
    url = 'http://flapi.nicovideo.jp/api/getflv/{}'.format(video_id)
    return session.get(url)

def download(session, video_id):
    # ダウンロード前に動画のページにアクセスする
    url = 'http://www.nicovideo.jp/watch/{}'.format(video_id)
    session.get(url)

    soup = BeautifulSoup(get_thumb_info(session, video_id).text, 'lxml')

    if soup.error:
        return print('Failed to get thumb info: {}'.format(video_id))

    title = soup.title.string
    movie_type = soup.movie_type.string

    qs_to_dict = lambda qs: dict(urllib.parse.parse_qsl(qs))
    flv = qs_to_dict(get_flv(session, video_id).text)

    res = session.get(flv['url'], stream=True)

    if res.status_code != 200:
        return print('Failed to download video: {}'.format(video_id))

    print('Start downloading: {}'.format(video_id))

    file_path = '{}/{}.{}'.format(VIDEOS_DIR, title, movie_type)
    with open(file_path, 'wb') as f:
        for chunk in res.iter_content(chunk_size=1024):
            f.write(chunk)

    print('Complete downloading: {}'.format(video_id))

def usage():
    print('Usage: python download.py <mail> <password> <video_id> [video_id...]')

def main():
    if len(sys.argv) < 4:
        return usage()

    session = requests.session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Safari/537.36',
    })

    login(session, sys.argv[1], sys.argv[2])

    if not is_logined(session):
        return print('failed to login.')

    os.makedirs(VIDEOS_DIR, exist_ok=True)

    for video_id in sys.argv[3:]:
        download(session, video_id)

if __name__ == '__main__':
    main()
