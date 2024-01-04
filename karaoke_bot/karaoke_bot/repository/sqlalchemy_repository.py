from sqlalchemy.orm import Session as Session_
from typing import Type, Any
from karaoke_bot.repository.abstract_repository import AbstractRepository, T
from karaoke_bot.models.sqlalchemy_models_without_polymorph import AlchemySession, TelegramProfile, Account,\
    Visitor, Moderator, Owner, Administrator, VisitorPerformance, Session, Karaoke, TrackVersion, Track, Artist
from karaoke_bot.models.sqlalchemy_exceptions import EmptyFieldError


class SQLAlchemyRepository:
    """
    Repository that works with a SQLAlchemy ORM.
    """
    table_name2model = {
        TelegramProfile.__tablename__: TelegramProfile,
        Account.__tablename__: Account,
        Visitor.__tablename__: Visitor,
        Moderator.__tablename__: Moderator,
        Owner.__tablename__: Owner,
        Administrator.__tablename__: Administrator,
        VisitorPerformance.__tablename__: VisitorPerformance,
        Session.__tablename__: Session,
        Karaoke.__tablename__: Karaoke,
        TrackVersion.__tablename__: TrackVersion,
        Track.__tablename__: Track,
        Artist.__tablename__: Artist
    }

    def __init__(self, alchemy_session: Session_) -> None:
        self.AlchemySession = alchemy_session

    def get(self, lookup_table_name: str, filter_by: dict, model_attr: list[str], search_attr: dict) -> dict:
        model_orm = self.table_name2model.get(lookup_table_name)
        if model_orm is None:
            raise KeyError(f'Не существует ORM модели с именем {lookup_table_name}')

        with AlchemySession() as session:
            model = session.query(model_orm).filter_by(**filter_by).first()

            if model is not None:
                for attr in model_attr:  # спускаемся по зависимостям и ищем нужную ORM модель
                    model = getattr(model, attr)
                    if model is None:
                        raise EmptyFieldError(table_name=attr.upper(), field_name=attr)

                return self._recursive_get_attr(model, search_attrs=search_attr)  # получаем аттрибуты у модели

            raise EmptyFieldError(table_name=model_orm.__tablename__, field_name='придумаю позже')

    def _recursive_get_attr(self, model, search_attrs: dict) -> dict:  # обходит вглубь словарь search_attrs
        data = {}
        for attr, sub_attrs in search_attrs.items():
            if hasattr(model, attr):
                attr_obj = getattr(model, attr)

                if not sub_attrs:  # Если словарь с податрибуттами пустой
                    data[attr] = attr_obj
                elif isinstance(attr_obj, list | set):
                    if 'field_name' in sub_attrs and 'func' in sub_attrs:
                        field_name = sub_attrs['field_name']
                        func = sub_attrs['func']
                        data[field_name] = func(attr_obj)
                    else:
                        data[attr] = [self._recursive_get_attr(item, sub_attrs) for item in attr_obj]
                else:
                    data[attr] = self._recursive_get_attr(attr_obj, sub_attrs)

        return data

    # example

    # data = Repository.get(
    #     lookup_table_name='telegram_profiles',
    #     filter_by={'id': message.from_user.id},
    #     model_attr=[
    #         'account',
    #         'visitor'
    #     ],
    #     search_attr={
    #         'karaokes': {
    #             'name': {},
    #             'owner': {
    #                 'account': {
    #                     'telegram_profile': {
    #                         'id': {},
    #                         'username': {}
    #                     }
    #                 }
    #             },
    #             'is_active': {},
    #             'avatar_id': {},
    #             'description': {},
    #             'subscribers': {
    #                 'field_name': 'subscribers_amount',
    #                 'func': len
    #             }
    #
    #         }
    #     }
    # )

    # def add(self, record_table_name: str, filter_by: dict, model_attr: list[str], search_attr: dict) -> None:
    #     model_orm = self.table_name2model.get(record_table_name)
    #     if model_orm is None:
    #         raise KeyError(f'Не существует ORM модели с именем {record_table_name}')
    #
    #     with AlchemySession() as session:
    #         model = session.query(model_orm).filter_by(**filter_by).first()
    #
    #         if model is not None:
    #             for attr in model_attr:  # спускаемся по зависимостям и ищем нужную ORM модель
    #                 model = getattr(model, attr)
    #                 if model is None:
    #                     raise EmptyFieldError(table_name=attr.upper(), field_name=attr)

    #
    # def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
    #     """Get all objects from the repository."""
    #     session = self.Session()
    #     if where is not None:
    #         query = session.query(self.cls).filter_by(**where)
    #     else:
    #         query = session.query(self.cls)
    #     return query.all()
    #
    # def update(self, obj: T) -> None:
    #     """Update object in the repository."""
    #     session = self.Session()
    #     session.merge(obj)
    #     session.commit()
    #
    # def delete(self, id: int) -> None:
    #     """Delete object from the repository by id."""
    #     session = self.Session()
    #     obj = session.query(self.cls).get(id)
    #     session.delete(obj)
    #     session.commit()
    #
    # def __del__(self) -> None:
    #     """Clean up resources."""
    #     self.engine.dispose()


Repository = SQLAlchemyRepository(alchemy_session=AlchemySession)
