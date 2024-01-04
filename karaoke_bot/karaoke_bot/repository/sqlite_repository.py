"""
SQLite repository class module.
"""
import sqlite3
from inspect import get_annotations
from typing import Type, Any
from karaoke_bot.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Repository that works with an SQLite database.
    """

    def __init__(self, db_file: str, cls: Type) -> None:
        self.db_file = db_file
        self.table_name = cls.__name__.lower()
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop("pk")

        # Аттрибуты для составления запроса метода add
        self._names = ', '.join(self.fields.keys())
        self._marks = ', '.join("?" * len(self.fields))

    def add(self, obj: T) -> int:
        """
        Add an object to the repo and return its id.
        """
        if getattr(obj, "pk", None) != 0:
            raise ValueError(f"trying to add object {obj} with filled 'pk' attribute")

        values = [getattr(obj, field) for field in self.fields]

        with sqlite3.connect(self.db_file) as connection:
            cur = connection.cursor()
            cur.execute("""PRAGMA foreign_keys = ON""")
            cur.execute(f"""INSERT INTO {self.table_name+'s'} ({self._names}) VALUES ({self._marks})""", values)
            pk = cur.lastrowid
            obj.pk = pk
        connection.close()
        return obj.pk

    def get(self, pk: int) -> T | None:
        """
        Get and object with a fixed id.
        """
        with sqlite3.connect(self.db_file) as connection:
            cur = connection.cursor()
            row = cur.execute(
                f"""SELECT * FROM {self.table_name} WHERE id=={pk}"""
            ).fetchone()
        connection.close()
        if not row:
            return None
        return self._covert_row(row)

    def get_all(self, where: dict[str, Any] | None = None) -> list[T] | None:
        """
        Get all entries that satisfy all "where" conditions, return all
        entries if where is None.
        where is a dictionary {"entry_field": value}
        """
        with sqlite3.connect(self.db_file) as connection:
            cur = connection.cursor()
            query = f"""SELECT * FROM {self.table_name}"""
            mark_replacements = []
            if where:
                fields = " AND ".join([f"{name} LIKE ?" for name in where])
                query += f" WHERE {fields}"
                mark_replacements = list(map(str, where.values()))
            rows = cur.execute(query, mark_replacements).fetchall()
        connection.close()
        if rows:
            res = [self._covert_row(row) for row in rows]
            return res
        return None

    def update(self, obj: T) -> None:
        """
        Update an entry with the same pk as the object.
        """
        if obj.pk == 0:
            raise ValueError("trying to update an object with no primary key")

        new_values = [getattr(obj, x) for x in self.fields]
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(
                f"""UPDATE {self.table_name} SET {self.fields_with_marks}
                WHERE id=={obj.pk}""",
                new_values,
            )
            if cur.rowcount == 0:
                raise ValueError(
                    "trying to update an object with an unknown primary key"
                )

        con.close()

    def delete(self, pk: int) -> None:
        """
        Remove an entry.
        """
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(f"""DELETE FROM {self.table_name} WHERE id=={pk}""")
        con.close()
