from aiogram.types import User
from typing import Type, List, Any
from .types import Track, TrackStatus, TrackWaited, YouTubeTrack, XMinusTrack


class KaraokeUser:

    def __init__(self, aiogram_user: User) -> None:
        self.id: int = aiogram_user.id
        self.aiogram_user = aiogram_user
        self.playlist: List[Track] = []
        self.removed_tracks: List[Track] = []
    #     self.next_track_waited = self.get_next_track_with_status(TrackWaited)
    #     self._switch_to_yield_none = True
    #
    # def get_next_track_with_status(self, status: Type[TrackStatus]) -> Track:
    #     while True:
    #         for track in self.playlist:
    #             if isinstance(track.status, status):
    #                 yield track
    #         while self._switch_to_yield_none:
    #             yield None
    #
    # def yield_none_switcher(self, switch: bool) -> None:
    #     self._switch_to_yield_none = switch

    def remove_track(self, track_id: int):
        track = self.find_first_match_track(where={'id': track_id})
        if track is not None:
            track.remove()
            self.playlist.remove(track)
            self.removed_tracks.append(track)

    def add_track_to_queue(self, track_url: str) -> None:
        if not isinstance(track_url, str):
            raise ValueError("Url should be an instance of <str>")
        track = self.get_track_instance(track_url)
        self.playlist.append(track)

    def pop_next_track(self) -> Track:
        return self.playlist.pop(0) if self.playlist else None

    @staticmethod
    def get_track_instance(track_url: str) -> Track:
        if 'youtube.com' in track_url or 'youtu.be' in track_url:
            return YouTubeTrack(track_url)

        if 'xminus.me' in track_url:
            return XMinusTrack(track_url)

    def find_first_match_track(self, where: dict[str, Any]) -> Track | None:
        # возвращает первое совпадение по условию
        for track in self.playlist:
            if all(getattr(track, attr) == value for attr, value in where.items()):
                return track

    def __str__(self) -> str:
        return f"KaraokeUser(id={self.id}, user={self.aiogram_user}, track_queue={list(self.playlist)})"

    def __repr__(self) -> str:
        return self.__str__()
