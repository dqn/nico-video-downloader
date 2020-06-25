import os
import requests
import sys
import urllib.parse

from bs4 import BeautifulSoup

VIDEOS_DIR = './videos'

class NicoVideoDownloaderExeption(Exception):
    pass

class NicoVideoDownloader:
    def __init__(self):
        self.session = requests.session()

    def login(self, mail, password):
        params = { 'mail_tel': mail, 'password': password }
        res = self.session.post('https://account.nicovideo.jp/api/v1/login', params=params)

        if res.headers['x-niconico-authflag'] != '1':
            raise NicoVideoDownloaderExeption('failed to login')

    def download(self, video_id):
        # Open the video page before downloading.
        self.session.get(f'https://www.nicovideo.jp/watch/{video_id}')

        video_info = self.__get_video_info(video_id)
        video_url = self.__get_video_url(video_id)

        print(f'downloading: {video_info["title"]}')

        res = self.session.get(video_url, stream=True)

        if res.status_code != 200:
            raise NicoVideoDownloaderExeption(res.text)

        filename = f'{video_info["title"]}.{video_info["movie_type"]}'
        filepath = os.path.join(VIDEOS_DIR, filename)

        with open(filepath, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024):
                f.write(chunk)

        print('completed!')

    def __get_video_info(self, video_id):
        res = self.session.get(f'https://ext.nicovideo.jp/api/getthumbinfo/{video_id}')

        if res.status_code != 200:
            raise NicoVideoDownloaderExeption(res.text)

        soup = BeautifulSoup(res.text, 'lxml')

        if soup.error:
            raise NicoVideoDownloaderExeption(res.text)

        return {
            'title': soup.title.string,
            'movie_type': soup.movie_type.string,
        }

    def __get_video_url(self, video_id):
        res = self.session.get(f'https://flapi.nicovideo.jp/api/getflv/{video_id}')
        flv = dict(urllib.parse.parse_qsl(res.text))

        return flv['url']

def usage():
    print('Usage: python3 download.py <mail> <password> <video-id>')

def run(mail, password, video_id):
    nico = NicoVideoDownloader()
    nico.login(mail, password)

    os.makedirs(VIDEOS_DIR, exist_ok=True)

    nico.download(video_id)

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
