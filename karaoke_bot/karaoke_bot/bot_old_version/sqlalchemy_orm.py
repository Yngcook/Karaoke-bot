from sqlalchemy import Integer, String, Boolean, DATETIME
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


Base = declarative_base()


class VisitorPerformance(Base):
    __tablename__ = 'visitor_performance'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(300))
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class Recommendations(Base):
    __tablename__ = 'recommendations'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer)
    message_id: Mapped[int] = mapped_column(Integer)
    url: Mapped[str] = mapped_column(String(300))
    rec_type: Mapped[str] = mapped_column(String(15))
    is_accepted: Mapped[bool] = mapped_column(Boolean)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

