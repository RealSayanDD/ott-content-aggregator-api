
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.association import title_genres


class Genre(Base):
    __tablename__ = "genres"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False
    )

    titles = relationship(
        "Title",
        secondary=title_genres,
        back_populates="genres"
    )
