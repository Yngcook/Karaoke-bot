from .sqlalchemy_models_without_polymorph import Karaoke, TelegramProfile, Account, AlchemySession, Owner, Visitor,\
    VisitorPerformance, Session, TrackVersion
from .sqlalchemy_exceptions import TelegramProfileNotFoundError, KaraokeNotFoundError, InvalidAccountStateError,\
    EmptyFieldError
from aiogram import types
from typing import List, Set


def create_or_update_telegram_profile(user: types.User) -> None:
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=user.id).first()
        if telegram_profile is not None:
            for field, value in user:
                if getattr(telegram_profile, field) != value:
                    setattr(telegram_profile, field, value)
                    print(f"ПОМЕНЯЛ {field} на {value}")
        else:
            telegram_profile = TelegramProfile(
                id=user.id,
                is_bot=user.is_bot,
                first_name=user.first_name,
                last_name=user.last_name,
                username=user.username,
                language_code=user.language_code,
                is_premium=user.is_premium
            )
            session.add(Account(telegram_profile=telegram_profile))
        session.commit()


def get_account_roles(telegram_id: int):
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account
            if account is not None:
                return account.is_visitor, account.is_owner, account.is_moderator, account.is_administrator

            raise EmptyFieldError('TelegramProfile', 'account')

        raise TelegramProfileNotFoundError(telegram_id)


def karaoke_not_exists(karaoke_name: str) -> bool:
    """
    Checks if a karaoke with the given name exists in the database.

    Parameters:
        karaoke_name (str): The name of the karaoke to check for existence.

    Returns:
        bool: True, if a karaoke with the specified name does not exist in the database,
              False, if the karaoke already exists.
    """
    with AlchemySession() as session:
        karaoke = session.query(Karaoke).filter_by(name=karaoke_name).scalar()
    return karaoke is None


def create_karaoke_session(karaoke_name: str) -> None:
    with AlchemySession() as session:
        karaoke = session.query(Karaoke).filter_by(name=karaoke_name).first()
        if karaoke is not None:
            karaoke.session = Session()
            session.commit()
        else:
            raise KaraokeNotFoundError(karaoke_name=karaoke_name)


def create_karaoke(telegram_id: int, name: str, avatar_id: str | None, description: str | None) -> None:
    with AlchemySession() as session:

        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account

            owner = account.owner
            if owner is None:
                account.is_owner = True
                owner = Owner(account=account)
                session.add(owner)

            owner.karaokes.add(Karaoke(name=name, is_active=True, avatar_id=avatar_id, description=description))
            session.commit()
        else:
            raise TelegramProfileNotFoundError(telegram_id)


def subscribe_to_karaoke(telegram_id: int, karaoke_name: str) -> None:
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account

            visitor = account.visitor
            if visitor is None:
                account.is_visitor = True
                visitor = Visitor(account=account)
                session.add(visitor)

            karaoke = session.query(Karaoke).filter_by(name=karaoke_name).first()
            if karaoke is not None:
                visitor.selected_karaoke = karaoke
                visitor.karaokes.add(karaoke)
                session.commit()
            else:
                session.commit()
                raise KaraokeNotFoundError(karaoke_name)
        else:
            raise TelegramProfileNotFoundError(telegram_id)


def get_karaoke_data_by_name(karaoke_name: str, user_id: int) -> dict:
    with AlchemySession() as session:
        karaoke = session.query(Karaoke).filter_by(name=karaoke_name).first()
        if karaoke is not None:
            avatar_id = karaoke.avatar_id
            description = karaoke.description
            owner_username = karaoke.owner.account.telegram_profile.username
            subscribers = karaoke.subscribers

            is_subscribed = False
            for visitor in subscribers:
                if user_id == visitor.account.telegram_profile.id:
                    is_subscribed = True
                    break

            data = {
                'avatar_id': avatar_id,
                'description': description,
                'owner': {
                    'username': owner_username
                },
                'subscribers': {
                    'amount': len(subscribers),
                    'is_subscribed': is_subscribed
                }
            }
            return data

        raise KaraokeNotFoundError(karaoke_name=karaoke_name)


def get_selected_karaoke_data(telegram_id: int) -> tuple:
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account
            visitor: Visitor = account.visitor
            if visitor is not None:
                selected_karaoke: Karaoke = visitor.selected_karaoke
                if selected_karaoke is not None:
                    return selected_karaoke.name, selected_karaoke.owner.account.telegram_profile.id

                raise EmptyFieldError('Visitor', 'selected_karaoke')

            raise InvalidAccountStateError(account_id=account.id, state='visitor')

        raise TelegramProfileNotFoundError(telegram_id=telegram_id)


def change_selected_karaoke(telegram_id: int, karaoke_name: str) -> None:
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account
            visitor: Visitor = account.visitor
            if visitor is not None:
                karaoke: Karaoke = session.query(Karaoke).filter_by(name=karaoke_name).first()
                if karaoke is not None:
                    visitor.selected_karaoke = karaoke
                    session.commit()
                else:
                    raise KaraokeNotFoundError(karaoke_name)
            else:
                raise InvalidAccountStateError(account_id=account.id, state='visitor')
        else:
            raise TelegramProfileNotFoundError(telegram_id=telegram_id)


def get_karaoke_owner_id(karaoke_name: str) -> int:
    with AlchemySession() as session:
        karaoke: Karaoke = session.query(Karaoke).filter_by(name=karaoke_name).first()
        if karaoke is not None:
            owner: Owner = karaoke.owner
            if owner is not None:
                account: Account = owner.account
                if account is not None:
                    telegram_profile: TelegramProfile = account.telegram_profile
                    if telegram_profile is not None:
                        return telegram_profile.id

                    raise EmptyFieldError('accounts', 'telegram_profile')

                raise EmptyFieldError('owners', 'account')

            raise EmptyFieldError('karaokes', 'owner')

        raise KaraokeNotFoundError(karaoke_name)


def add_performance_to_visitor(telegram_id: int, track_url: str):
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account
            visitor: Visitor = account.visitor
            if visitor is not None:
                selected_karaoke: Karaoke = visitor.selected_karaoke
                if selected_karaoke is not None:
                    session.add(
                        VisitorPerformance(
                            visitor_id=visitor.account_id,
                            track_version=TrackVersion(url=track_url),
                            session_id=selected_karaoke.session.id
                        )
                    )
                    session.commit()
                else:
                    raise EmptyFieldError('Visitor', 'selected_karaoke')
            else:
                raise InvalidAccountStateError(account_id=account.id, state='visitor')
        else:
            raise TelegramProfileNotFoundError(telegram_id)


def get_visitor_karaoke_names(telegram_id: int) -> set:
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account
            visitor: Visitor = account.visitor
            if visitor is not None:
                karaokes = visitor.karaokes
                if karaokes is not None:
                    return {karaoke.name for karaoke in karaokes}

                raise EmptyFieldError('Visitor', 'karaokes')

            raise InvalidAccountStateError(account_id=account.id, state='visitor')

        raise TelegramProfileNotFoundError(telegram_id=telegram_id)


def get_visitor_karaokes_data(telegram_id: int) -> dict[str]:
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account
            visitor: Visitor = account.visitor
            if visitor is not None:
                karaokes: List[Karaoke] = visitor.karaokes
                if karaokes is not None:
                    data = {}
                    for karaoke in karaokes:
                        telegram_profile: TelegramProfile = karaoke.owner.account.telegram_profile

                        data[karaoke.name] = {
                            'owner': {
                                'id': telegram_profile.id,
                                'username': telegram_profile.username
                            },
                            'is_active': karaoke.is_active,
                            'subscribers_amount': len(karaoke.subscribers),
                            'avatar_id': karaoke.avatar_id,
                            'description': karaoke.description
                        }
                    return data

                raise EmptyFieldError('Visitor', 'karaokes')

            raise InvalidAccountStateError(account_id=account.id, state='visitor')

        raise TelegramProfileNotFoundError(telegram_id=telegram_id)


def get_owner_karaokes_data(telegram_id: int) -> dict[str]:
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account: Account = telegram_profile.account
            owner: Owner = account.owner
            if owner is not None:
                karaokes: Set[Karaoke] = owner.karaokes
                if karaokes is not None:
                    data = {}
                    for karaoke in karaokes:
                        data[karaoke.name] = {
                            'is_active': karaoke.is_active,
                            'subscribers_amount': len(karaoke.subscribers),
                            'avatar_id': karaoke.avatar_id,
                            'description': karaoke.description
                        }
                    return data

                raise EmptyFieldError('Owner', 'karaokes')

            raise InvalidAccountStateError(account_id=account.id, state='owner')

        raise TelegramProfileNotFoundError(telegram_id=telegram_id)