from uuid import uuid4, UUID
from sqlalchemy.orm import Mapped, mapped_column
from . import Base
import datetime


class Message(Base):
    __tablename__ = "message_table"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    chat_id: Mapped[str] = mapped_column()
    message_id: Mapped[str] = mapped_column()
    message_text: Mapped[str] = mapped_column(nullable=True)
    timestamp: Mapped[datetime.datetime] = mapped_column()

    def __repr__(self) -> str:
        return f"Message(id={self.id}, chat_id={self.chat_id} message_id={self.message_id} timestamp={self.timestamp})"

