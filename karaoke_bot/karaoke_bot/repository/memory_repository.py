"""
Модуль описывает репозиторий, работающий в оперативной памяти
"""

from itertools import count
from typing import Any

from karaoke_bot.repository.abstract_repository import AbstractRepository, T


class MemoryRepository(AbstractRepository[T]):
    """
    Репозиторий, работающий в оперативной памяти. Хранит данные в словаре.
    MemoryRepository может быть полезен в некоторых случаях, когда нет необходимости использовать реальную базу данных.
    Например, в тестировании, отладке или прототипировании,
    когда требуется временное хранение данных только в оперативной памяти.
    Он также может использоваться для реализации временного хранилища данных,
    которое не требует постоянного сохранения данных после завершения работы приложения.
    """

    def __init__(self) -> None:
        self._container: dict[int, T] = {}
        self._counter = count(1)

    def add(self, obj: T) -> int:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f'trying to add object {obj} with filled `pk` attribute')
        pk = next(self._counter)
        self._container[pk] = obj
        obj.pk = pk
        return pk

    def get(self, pk: int) -> T | None:
        return self._container.get(pk)

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        if where is None:
            return list(self._container.values())
        return [obj for obj in self._container.values()
                if all(getattr(obj, attr) == value for attr, value in where.items())]

    def update(self, obj: T) -> None:
        if obj.pk == 0:
            raise ValueError('attempt to update object with unknown primary key')
        self._container[obj.pk] = obj

    def delete(self, pk: int) -> None:
        self._container.pop(pk)