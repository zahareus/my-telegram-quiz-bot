from uuid import uuid4, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint
from . import Base
import datetime


class Channel(Base):
    __tablename__ = "channel_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    channel_id: Mapped[str] = mapped_column(unique=True)
    channel_title: Mapped[str] = mapped_column(nullable=True)
    is_daily: Mapped[bool] = mapped_column(default=False)
    is_weekly: Mapped[bool] = mapped_column(default=False)
    is_active: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"Channel(id={self.id}, chat_id={self.channel_id})"


class User(Base):
    __tablename__ = "user_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(unique=True)
    username: Mapped[str] = mapped_column(nullable=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"User(id={self.id}, user_id={self.user_id})"


class Message(Base):
    __tablename__ = "message_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    message_id: Mapped[str] = mapped_column()
    message_text: Mapped[str] = mapped_column(nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column()

    channel_id: Mapped[UUID] = mapped_column(ForeignKey("channel_table.id"))
    channel: Mapped[Channel] = relationship(lazy="selectin")

    def __repr__(self) -> str:
        return f"Message(id={self.id}, chat_id={self.channel_id} message_id={self.message_id} timestamp={self.timestamp})"


class ChannelEditor(Base):
    __tablename__ = "channel_editor_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    channel_id: Mapped[UUID] = mapped_column(ForeignKey("channel_table.id"))
    channel: Mapped[Channel] = relationship(lazy="selectin")

    user_id: Mapped[UUID] = mapped_column(ForeignKey("user_table.id"))
    user: Mapped[User] = relationship(lazy="selectin")

    __table_args__ = (
        UniqueConstraint("channel_id", "user_id", name="uq_chat_user_pair"),
    )

    def __repr__(self) -> str:
        return f"ChannelEditor(id={self.id}, channel_id={self.channel_id} user_id={self.user_id})"
