import argparse
import time
from typing import Dict

import yt_dlp.utils

from music2vec.music2vec.extraction import Extractor
from music2vec.music2vec.dataset import GENRES
from yt_dlp import YoutubeDL
import os
import csv
import json


class YouTubeTrackDownloader:

    def __init__(self, url):
        self.url = url
        self.info: Dict[str, str] = {}
        self.filename: str = ''
        self.abspath = ''
        self.genres = None
        self.features = None
        self.extractor = Extractor()

    def get_info(self) -> Dict[str, str]:
        if not self.info:
            ydl_opts = {'quiet': True}
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                self.info = {
                    'video_id': info.get('id', ''),
                    'title': info.get('title', ''),
                    'uploader': info.get('uploader', ''),
                    'description': info.get('description', ''),
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'comment_count': info.get('comment_count', 0),
                    'categories': info.get('categories', [])
                }
        return self.info

    def download(self) -> str:
        outtmpl = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracks_wav', '%(id)s.%(ext)s')
        cachedir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tracks_cache')
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '192',
            }],
            'outtmpl': outtmpl,
            'cachedir': cachedir,
            'noplaylist': True,
            'extractaudio': True,
            'no_cache_dir': True,
            'quiet': True
        }
        with YoutubeDL(ydl_opts) as ydl:
            # error_code = ydl.download(url)
            info = ydl.extract_info(self.url, download=True)

        self.filename = 'tracks_wav/' + info.get('id') + '.wav'

        # # нужно если в имени файла есть слэши
        # old_filepath = os.path.join('tracks_wav', self.filename)
        # self.filename = self.filename.replace('/', '')
        # new_filepath = os.path.join('tracks_wav', self.filename)
        # os.rename(old_filepath, new_filepath)

        # self.abspath = os.path.abspath(self.filename)
        # print(self.abspath)
        return self.filename

    def wav2vec(self, filepath):
        self.genres, self.features = self.extractor(filepath)
        return self.genres, self.features

    def __str__(self) -> str:
        return f"YouTubeTrack: title - {self.info['title']} id - {self.info['video_id']}"

    def __repr__(self) -> str:
        return f"YouTubeTrack(url='{self.url}')"


def create_parser():
    parser = argparse.ArgumentParser()

    subparsers = parser.add_subparsers(
        title='subcommands',
        description="All subcommands",
        help="When typing a subcommand, the corresponding function of the same name will be called.",
        dest='subparser_name')

    parser_download = subparsers.add_parser('dwld')
    parser_download.add_argument('link', type=str)

    parser_music2vec = subparsers.add_parser('m2v')
    parser_music2vec.add_argument('filepath', type=str)

    parser_convert = subparsers.add_parser('convert')
    parser_convert.add_argument('link')
    return parser


if __name__ == "__main__":
    parser = create_parser()
    args = parser.parse_args()

    # if args.subparser_name == 'dwld':
    #     # print(json.dumps(download_video_youtube(url=args.link), indent=4))
    #     print(download_video_youtube(url=args.link))
    #
    # if args.subparser_name == 'm2v':
    #     wav2vec(file_wav=args.filepath)

    with open('id_url.csv', encoding='utf-8') as file:
        rows = list(csv.DictReader(file))


    all_urls = []
    tracks = []
    for row in rows:
        track = YouTubeTrackDownloader(row['url'])

        if track.url not in all_urls:
            all_urls.append(track.url)

            with open('tracks_data.json', encoding='utf-8') as file:
                tracks_data = json.load(file)

            if 'xminus' not in track.url:
                try:
                    track_info = track.get_info()
                    track_info['url'] = track.url
                    track_info['genre_vector'] = {}

                    time.sleep(5)

                    filepath = track.download()
                    genre_values, features = track.wav2vec(filepath)

                    for genre, value in zip(GENRES, genre_values):
                        track_info['genre_vector'][genre] = round(float(value), 4)

                except yt_dlp.utils.DownloadError:
                    track_info = {'url': track.url, 'error': 'DownloadError'}
            else:
                track_info = {'url': track.url}

            tracks_data.append(track_info)
            with open('tracks_data.json', 'w', encoding='utf-8') as file:
                json.dump(tracks_data, file, ensure_ascii=False, indent=2)

            time.sleep(5)
