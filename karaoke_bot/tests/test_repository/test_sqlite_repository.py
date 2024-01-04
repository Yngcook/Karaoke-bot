"""
SQLite repository class tests.
"""
from dataclasses import dataclass
import os
import pytest

from karaoke_bot.repository.sqlite_repository import SQLiteRepository


@pytest.fixture(name="custom_class")
def fixture_custom_class():
    """
    A fixture of a model of a class for repo.
    """

    @dataclass
    class Custom:
        col1: int = 1
        col2: str = "foo"
        pk: int = 0

    return Custom


@pytest.fixture(name="repo")
def fixture_repository(custom_class):
    """
    A fixture to text repository integration of the class.
    """
    db_path = "databases/test_sql.db"
    os.remove(db_path)
    temp = open(db_path, "a", encoding="utf-8")
    temp.close()
    return SQLiteRepository[custom_class](db_path, custom_class)


def test_crud(repo: SQLiteRepository, custom_class):
    """
    All CRUD operations should be performed correctly.
    """
    # create
    obj = custom_class(1, "foo")
    pk = repo.add(obj)
    assert pk == obj.pk
    # read
    assert repo.get(pk) == obj
    # update
    obj2 = custom_class(col1=11, col2="bar", pk=pk)
    repo.update(obj2)
    assert repo.get(pk) == obj2
    # delete
    repo.delete(pk)
    assert repo.get(pk) is None


def test_cannot_add_with_pk(repo: SQLiteRepository, custom_class):
    """
    An object can't have a pk when being added.
    """
    obj = custom_class(col1=1, col2="foo", pk=1)
    with pytest.raises(ValueError):
        repo.add(obj)


def test_cannot_add_without_pk(repo: SQLiteRepository):
    """
    An object must have a pk attribute to be added.
    """
    with pytest.raises(ValueError):
        repo.add(0)


def test_cannot_update_unexistent(repo: SQLiteRepository, custom_class):
    """
    Shouldn't be able to update an entry with a pk that doesn't exist.
    """
    obj = custom_class(pk=100)
    with pytest.raises(ValueError):
        repo.update(obj)


def test_cannot_update_without_pk(repo: SQLiteRepository, custom_class):
    """
    An object must have a pk when being a template for an update.
    """
    obj = custom_class()
    with pytest.raises(ValueError):
        repo.update(obj)


def test_get_unexistent(repo: SQLiteRepository):
    """
    Shouldn't be able to get something that isn't there.
    """
    assert repo.get(-1) is None


def test_get_all(repo: SQLiteRepository, custom_class):
    """
    Getting entries of the repo should work correctly.
    """
    objects = [custom_class(col2=str(i)) for i in range(5)]
    _ = [repo.add(o) for o in objects]
    assert objects == repo.get_all_where()


def test_get_all_with_condition(repo: SQLiteRepository, custom_class):
    """
    Getting entries of the repo should work correctly.
    """
    objects = [custom_class(i, "test") for i in range(5)]
    _ = [repo.add(o) for o in objects]
    assert [objects[0]] == repo.get_all_where({"col1": 0, "col2": "test"})
    assert objects == repo.get_all_where({"col2": "test"})
    assert repo.get_all_where({"col2": "random"}) is None