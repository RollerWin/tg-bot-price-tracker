from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class CheckInterval(Base):
    __tablename__ = 'check_intervals'

    id: Mapped[int] = mapped_column(primary_key=True)
    # user_id: Mapped[int] = mapped_column(ForeignKey('users.id'))
    user_id: Mapped[int] = mapped_column(nullable=False)
    interval: Mapped[int] = mapped_column(nullable=False)
