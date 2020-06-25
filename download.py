import sys
import os
import requests
import urllib.parse
from bs4 import BeautifulSoup

VIDEOS_DIR = './videos'

def usage():
    print('Usage: python3 download.py <mail> <password> <video-id>')

def login(session, mail, password):
    url = 'https://account.nicovideo.jp/api/v1/login'
    params = { 'mail_tel': mail, 'password': password }
    res = session.post(url, params=params)

    if res.headers['x-niconico-authflag'] != '1':
        raise Exception('failed to login')

def download(session, video_id):
    # Open the video page before downloading.
    session.get(f'http://www.nicovideo.jp/watch/{video_id}')

    thumb_info = session.get(f'http://ext.nicovideo.jp/api/getthumbinfo/{video_id}').text
    soup = BeautifulSoup(thumb_info, 'lxml')

    if soup.error:
        raise Exception(thumb_info)

    title = soup.title.string
    movie_type = soup.movie_type.string

    flv = session.get(f'http://flapi.nicovideo.jp/api/getflv/{video_id}').text

    qs_to_dict = lambda qs: dict(urllib.parse.parse_qsl(qs))
    flv = qs_to_dict(flv)

    print(f'downloading: {title}')

    res = session.get(flv['url'], stream=True)

    if res.status_code != 200:
        raise Exception(res.text)

    file_path = os.path.join(VIDEOS_DIR, f'{title}.{movie_type}')
    with open(file_path, 'wb') as f:
        for chunk in res.iter_content(chunk_size=1024):
            f.write(chunk)

    print('completed!')

def run(mail, password, video_id):
    session = requests.session()

    login(session, mail, password)

    os.makedirs(VIDEOS_DIR, exist_ok=True)
    download(session, video_id)

def main():
    if len(sys.argv) != 4:
        usage()
        sys.exit(1)

    try:
        run(*sys.argv[1:])
    except Exception as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
