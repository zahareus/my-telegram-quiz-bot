from uuid import uuid4, UUID
from sqlalchemy.orm import Mapped, mapped_column
from . import Base
import datetime


class Message(Base):
    __tablename__ = "message_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)

    message_id: Mapped[str] = mapped_column()
    message_text: Mapped[str] = mapped_column(nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column()

    chat: Mapped["Chat"] = mapped_column("Chat", back_populates="messages")
    chat_id: Mapped[str] = mapped_column()

    def __repr__(self) -> str:
        return f"Message(id={self.id}, chat_id={self.chat_id} message_id={self.message_id} timestamp={self.timestamp})"


class Chat(Base):
    __tablename__ = "chat_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    chat_id: Mapped[str] = mapped_column(unique=True)
    is_daily: Mapped[bool] = mapped_column(default=False)
    is_weekly: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"Chat(id={self.id}, chat_id={self.chat_id})"


class User(Base):
    __tablename__ = "user_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[str] = mapped_column(unique=True)
    is_admin: Mapped[bool] = mapped_column(default=False)

    def __repr__(self) -> str:
        return f"User(id={self.id}, user_id={self.user_id})"
