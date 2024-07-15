from datetime import datetime

from sqlalchemy import ForeignKey
from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class PriceLog  (Base):
    __tablename__ = 'price_logs'

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(ForeignKey('products.id'))
    price: Mapped[float] = mapped_column(default=0)
    timestamp: Mapped[datetime] = mapped_column(nullable=False)
