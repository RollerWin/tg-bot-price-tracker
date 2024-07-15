from sqlalchemy.orm import mapped_column, Mapped

from .base import Base


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    is_available: Mapped[bool] = mapped_column(nullable=False)
    price: Mapped[float] = mapped_column(nullable=True)
    quantity: Mapped[int] = mapped_column(nullable=True)
    url: Mapped[str] = mapped_column(nullable=False)
