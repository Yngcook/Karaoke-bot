from aiogram.types import User
from typing import Type, List, Any, Tuple
from .types import Track, TrackStatus, TrackWaited, YouTubeTrack, XMinusTrack
from .karaoke_user import KaraokeUser


class Karaoke:
    def __init__(self, name: str, owner_id: int):
        self.name = name
        self.owner_id = owner_id
        self.user_queue: List[KaraokeUser] = []
    #     self.track_num: int = 1
    #     self.next_round = self.get_next_round()

    def how_many_laps(self) -> int:
        return max(len(user.playlist) for user in self.user_queue)

    def get_lap_queue(self, lap_number: int) -> List[Tuple[KaraokeUser, Track]]:
        lap = []
        for user in self.user_queue:
            try:
                track = user.playlist[lap_number]
            except IndexError:
                continue
            else:
                if isinstance(track.status, TrackWaited):
                    lap.append((user, track))
        return lap

    # def get_next_round(self):
    #     while True:
    #         round_queue = self._get_next_round_queue()
    #
    #         if not round_queue:  # либо конец очереди, либо треков вообще нет
    #             # организовать удаление
    #             self._yield_none_switcher(False)
    #             round_queue = self._get_next_round_queue()  # проверяем ещё раз, если это был конец очереди
    #             self._yield_none_switcher(True)
    #         yield round_queue
    #
    # def _get_next_round_queue(self):
    #     round_queue = []
    #     for user in self.user_queue:
    #         track = next(user.next_track_waited)
    #         if track is not None:
    #             round_queue.append((user, track))
    #     return round_queue
    #
    # def _yield_none_switcher(self, switch: bool) -> None:
    #     for user in self.user_queue:
    #         user.yield_none_switcher(switch)

    def add_user_to_queue(self, user: KaraokeUser) -> None:
        if not isinstance(user, KaraokeUser):
            raise ValueError("User should be an instance of KaraokeUser")
        self.user_queue.append(user)

    def pop_next_user(self) -> KaraokeUser:
        return self.user_queue.pop(0) if self.user_queue else None

    def find_first_match_user(self, where: dict[str, Any]) -> KaraokeUser:
        # возвращает первое совпадение по условию
        for user in self.user_queue:
            if all(getattr(user, attr) == value for attr, value in where.items()):
                return user

    def find_first_user_by_track(self, where: dict[str, Any]) -> Tuple[KaraokeUser, Track] | None:
        # возвращает первое совпадение по условию
        for user in self.user_queue:
            track = user.find_first_match_track(where=where)
            if track is not None:
                return user, track

    def __str__(self) -> str:
        return f"Karaoke(name={self.name}, user_queue={list(self.user_queue)})"

    def __repr__(self) -> str:
        return self.__str__()


def find_first_match_karaoke(karaoke_name: str) -> Karaoke:
    # генератор возвращает первое совпадение по имени
    return next((karaoke for karaoke in ready_to_play_karaoke_list if karaoke.name == karaoke_name), None)


def add_track_to_queue(user: User, karaoke_name: str, owner_id: int, track_url: str) -> None:

    karaoke = find_first_match_karaoke(karaoke_name)
    if karaoke is None:  # Караоке ещё нет в списке
        karaoke = Karaoke(karaoke_name, owner_id)
        ready_to_play_karaoke_list.append(karaoke)

    karaoke_user = karaoke.find_first_match_user(where={'id': user.id})
    if karaoke_user is None:  # Караоке есть, но такого пользователя в нем нет.
        karaoke_user = KaraokeUser(user)
        karaoke.add_user_to_queue(karaoke_user)

    karaoke_user.add_track_to_queue(track_url)
    print(ready_to_play_karaoke_list)


ready_to_play_karaoke_list: List[Karaoke] = []
