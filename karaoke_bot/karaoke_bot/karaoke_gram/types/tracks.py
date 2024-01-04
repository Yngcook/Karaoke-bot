from yt_dlp import YoutubeDL
from typing import Dict
from .track_status import TrackStatus, TrackWaited, TrackRemoved


class Track:
    _track_counter = 0  # Счетчик для порядковых номеров треков (id)

    def __new__(cls, url):
        instance = super(Track, cls).__new__(cls)
        Track._track_counter += 1
        instance.id = Track._track_counter
        return instance

    def __init__(self, url):
        self.url = url
        self.status: TrackStatus = TrackWaited()
        self.info: Dict[str, str] = {}

    def get_info(self):
        raise NotImplementedError

    def remove(self):
        self.status = TrackRemoved()

    def __str__(self):
        pass

    def __repr__(self):
        pass


class YouTubeTrack(Track):

    def __init__(self, url: str):
        super().__init__(url)

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

    def __str__(self) -> str:
        return f"YouTubeTrack: title - {self.info['title']} id - {self.info['video_id']}"

    def __repr__(self) -> str:
        return f"YouTubeTrack(url='{self.url}')"


class XMinusTrack(Track):
    def __init__(self, url: str):
        super().__init__(url)

    def get_info(self):
        if not self.info:
            # логика для получения информации о треке на xminus.com
            pass
        return self.info

    def __str__(self) -> str:
        return f"XMinusTrack: url - {self.url}"

    def __repr__(self) -> str:
        return f"XMinusTrack(url='{self.url}')"


if __name__ == '__main__':
    track_url = input("Введите URL видео на YouTube: ")
    track = YouTubeTrack(track_url)

    for key, value in track.get_info().items():
        print(f"{key}: {value}")

    # info = ydl.extract_info(url, download=False)
    # print(json.dumps(ydl.sanitize_info(info), indent=2))
