from .karaoke import Karaoke
from typing import Any, List
from .types import Track


def find_first_match_karaoke(karaokes: List[Karaoke], where: dict[str, Any]) -> Karaoke:
    # возвращает первое совпадение по условию
    for karaoke in karaokes:
        if all(getattr(karaoke, attr) == value for attr, value in where.items()):
            return karaoke


def find_first_match_user(karaokes: List[Karaoke], where: dict[str, Any]) -> Karaoke:
    # возвращает первое совпадение по условию
    for karaoke in karaokes:
        if all(getattr(karaoke, attr) == value for attr, value in where.items()):
            return karaoke


def find_first_match_track(playlist: List[Track], where: dict[str, Any]) -> Track:
    # возвращает первое совпадение по условию
    for track in playlist:
        if all(getattr(track, attr) == value for attr, value in where.items()):
            return track
