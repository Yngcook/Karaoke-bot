from typing import Set, List
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, DateTime, ForeignKey, TIMESTAMP, func, DATETIME
from sqlalchemy.orm import Mapped, mapped_column, relationship, declarative_base, column_property, sessionmaker

Base = declarative_base()


class TelegramProfile(Base):
    __tablename__ = 'telegram_profiles'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), unique=True, nullable=False)
    id: Mapped[int] = mapped_column(primary_key=True)
    is_bot: Mapped[bool]
    first_name: Mapped[str] = mapped_column(String(64))
    last_name: Mapped[str] = mapped_column(String(64), nullable=True)
    username: Mapped[str] = mapped_column(String(32), nullable=True)
    language_code: Mapped[str] = mapped_column(String(10))
    is_premium: Mapped[bool] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    account: Mapped["Account"] = relationship(back_populates='telegram_profile')


class Account(Base):
    __tablename__ = 'accounts'

    id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    is_visitor: Mapped[bool] = mapped_column(nullable=True)
    is_owner: Mapped[bool] = mapped_column(nullable=True)
    is_moderator: Mapped[bool] = mapped_column(nullable=True)
    is_administrator: Mapped[bool] = mapped_column(nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    telegram_profile: Mapped["TelegramProfile"] = relationship(back_populates='account')
    visitor: Mapped["Visitor"] = relationship(back_populates='account')
    owner: Mapped["Owner"] = relationship(back_populates='account')
    moderator: Mapped["Moderator"] = relationship(back_populates='account')
    administrator: Mapped["Administrator"] = relationship(back_populates='account')

    def __repr__(self):
        return (
            f"<Account(\n"
            f"  id={self.id},\n"
            f"  is_visitor={self.is_visitor},\n"
            f"  is_owner={self.is_owner},\n"
            f"  is_moderator={self.is_moderator},\n"
            f"  is_administrator={self.is_administrator},\n"
            f"  created_at={self.created_at},\n"
            f"  updated_at={self.updated_at}\n"
            f")>"
        )


visitors_karaokes = Table(
    'visitors_karaokes',
    Base.metadata,
    Column('visitor_id', Integer, ForeignKey('visitors.account_id')),
    Column('karaoke_id', Integer, ForeignKey('karaokes.id'))
)


class Visitor(Base):
    __tablename__ = 'visitors'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    selected_karaoke_id: Mapped[int] = mapped_column(ForeignKey('karaokes.id'), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())

    account: Mapped["Account"] = relationship(back_populates='visitor')
    selected_karaoke: Mapped["Karaoke"] = relationship()
    karaokes: Mapped[Set["Karaoke"]] = relationship(secondary=visitors_karaokes, back_populates='subscribers')
    performances: Mapped[List["VisitorPerformance"]] = relationship(back_populates='visitor')

    def __repr__(self):
        return (
            f"<Visitor(\n"
            f"  account_id={self.account_id},\n"
            f"  selected_karaoke_id={self.selected_karaoke_id},\n"
            f"  created_at={self.created_at},\n"
            f"  updated_at={self.updated_at}\n"
            f")>"
        )


class Moderator(Base):
    __tablename__ = 'moderators'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    karaoke_id: Mapped[int] = mapped_column(ForeignKey('karaokes.id'))
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    account: Mapped["Account"] = relationship(back_populates='moderator')
    karaoke: Mapped["Karaoke"] = relationship(back_populates='moderators')


class Owner(Base):
    __tablename__ = 'owners'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    # password: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    account: Mapped["Account"] = relationship(back_populates='owner')
    karaokes: Mapped[Set["Karaoke"]] = relationship(back_populates='owner')


class Administrator(Base):
    __tablename__ = 'administrators'

    account_id: Mapped[int] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 nullable=False,
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    account: Mapped["Account"] = relationship(back_populates='administrator')


class VisitorPerformance(Base):
    __tablename__ = 'visitor_performances'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    visitor_id: Mapped[int] = mapped_column(ForeignKey('visitors.account_id'))
    track_version_id: Mapped[int] = mapped_column(ForeignKey('track_versions.id'))
    session_id: Mapped[int] = mapped_column(ForeignKey('sessions.id'))

    visitor: Mapped["Visitor"] = relationship(back_populates='performances')
    session: Mapped["Session"] = relationship(back_populates='performance')
    track_version: Mapped["TrackVersion"] = relationship(back_populates='performances')


class Session(Base):
    __tablename__ = 'sessions'

    id: Mapped[int] = mapped_column(primary_key=True)
    karaoke_id: Mapped[int] = mapped_column(ForeignKey('karaokes.id'))
    timestamp_from: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    timestamp_to: Mapped[DateTime] = mapped_column(DATETIME, nullable=True)

    performance: Mapped["VisitorPerformance"] = relationship(back_populates='session')
    karaoke: Mapped["Karaoke"] = relationship(back_populates='session')


class Karaoke(Base):
    __tablename__ = 'karaokes'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True)
    is_active: Mapped[bool]
    owner_id: Mapped[int] = mapped_column(ForeignKey('owners.account_id'))
    avatar_id: Mapped[str] = mapped_column(String(150), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )

    subscribers: Mapped[Set["Visitor"]] = relationship(secondary=visitors_karaokes, back_populates='karaokes')

    moderators: Mapped[Set["Moderator"]] = relationship(back_populates='karaoke')
    owner: Mapped["Owner"] = relationship(back_populates='karaokes')
    session: Mapped["Session"] = relationship(back_populates='karaoke')


class TrackVersion(Base):
    __tablename__ = 'track_versions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    track_id: Mapped[int] = mapped_column(ForeignKey('tracks.id'), nullable=True)
    url: Mapped[str] = mapped_column(String(2048), index=True)
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp()
    )
    performances: Mapped[List["VisitorPerformance"]] = relationship(back_populates='track_version')
    track: Mapped["Track"] = relationship(back_populates='versions')


tracks_artists = Table(
    'tracks_artists',
    Base.metadata,
    Column('track_id', Integer, ForeignKey('tracks.id')),
    Column('artist_id', Integer, ForeignKey('artist.id'))
)


class Track(Base):
    __tablename__ = 'tracks'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[DateTime] = mapped_column(DATETIME, server_default=func.now())
    updated_at: Mapped[DateTime] = mapped_column(TIMESTAMP(timezone=True),
                                                 server_default=func.current_timestamp(),
                                                 onupdate=func.current_timestamp())
    versions: Mapped[Set["TrackVersion"]] = relationship(back_populates='track')
    artists: Mapped[Set["Artist"]] = relationship(secondary=tracks_artists, back_populates="tracks")


class Artist(Base):
    __tablename__ = 'artist'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(64))
    tracks: Mapped[Set["Track"]] = relationship(secondary=tracks_artists, back_populates="artists")


# engine = create_engine('mysql+pymysql://karaoke_bot:karaoke_bot@localhost/karaoke_db', echo=True)
engine = create_engine('sqlite:///karaoke_sqlaclhemy.db', echo=True)
Base.metadata.create_all(engine)
AlchemySession = sessionmaker(bind=engine)


def sqlalchemy_create_account(id, first_name, last_name, username):
    with AlchemySession() as session:
        telegram_profile = TelegramProfile(
            id=id,
            is_bot=False,
            first_name=first_name,
            last_name=last_name,
            username=username,
            language_code='en',
            is_premium=True
        )
        account = Account(
            telegram_profile=telegram_profile
        )
        session.add(account)
        session.commit()


def sqlalchemy_add_role(telegram_id: int, role: str):
    with AlchemySession() as session:
        telegram_profile = session.query(TelegramProfile).filter_by(id=telegram_id).first()
        if telegram_profile is not None:
            account = telegram_profile.account
            match role:
                case 'visitor':
                    account.is_visitor = True
                    account.visitor = Visitor(selected_karaoke_id=1)
                case 'owner':
                    pass
                case 'administrator':
                    pass
                case 'moderator':
                    pass

            session.commit()
        else:
            print("Telegram profile not found.")


if __name__ == '__main__':
    sqlalchemy_create_account(id=1234, first_name='Petr', last_name='Grachev', username='gra4evp')
    # sqlalchemy_add_role(telegram_id=1234, role='visitor')
