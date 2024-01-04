import pymysql
from typing import Any, Type
from karaoke_bot.repository.abstract_repository import AbstractRepository, T


class MySQLRepository(AbstractRepository[T]):
    """
    Repository that works with a MySQL database.
    """

    def __init__(self, host: str, user: str, password: str, database: str, cls: Type) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.cls = cls
        self.table_name = cls.__name__.lower()
        self.connection = pymysql.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.connection.cursor()
        self.fields = [field[0] for field in self.cursor.description]

    def add(self, obj: T) -> int:
        """Add object to the repository and return the id of the object."""
        data = [getattr(obj, field) for field in self.fields if field != "pk"]
        columns = ",".join(self.fields)
        placeholders = ",".join(["%s"] * (len(self.fields) - 1))
        query = f"INSERT INTO {self.table_name} ({columns}) VALUES ({placeholders})"
        self.cursor.execute(query, data)
        self.connection.commit()
        obj.pk = self.cursor.lastrowid
        return obj.pk

    def get(self, pk: int) -> T | None:
        """Get object from the repository by id."""
        query = f"SELECT * FROM {self.table_name} WHERE pk = %s"
        self.cursor.execute(query, (pk,))
        row = self.cursor.fetchone()
        if row is not None:
            obj = self.cls(**dict(zip(self.fields, row)))
            return obj
        else:
            return None

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """Get all objects from the repository."""
        query = f"SELECT * FROM {self.table_name}"
        params = ()
        if where is not None:
            conditions = []
            for field, value in where.items():
                conditions.append(f"{field} = %s")
                params += (value,)
            query += " WHERE " + " AND ".join(conditions)
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        objects = []
        for row in rows:
            obj = self.cls(**dict(zip(self.fields, row)))
            objects.append(obj)
        return objects

    def update(self, obj: T) -> None:
        """Update object in the repository."""
        data = [getattr(obj, field) for field in self.fields if field != "pk"]
        columns = ",".join([field + " = %s" for field in self.fields if field != "pk"])
        query = f"UPDATE {self.table_name} SET {columns} WHERE pk = %s"
        data.append(obj.pk)
        self.cursor.execute(query, tuple(data))
        self.connection.commit()

    def delete(self, pk: int) -> None:
        """Delete object from the repository by id."""
        query = f"DELETE FROM {self.table_name} WHERE pk = %s"
        self.cursor.execute(query, (pk,))
        self.connection.commit()

    def __del__(self) -> None:
        """Clean up resources."""
        self.cursor.close()
        self.connection.close()
