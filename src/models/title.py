
from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.association import title_genres, title_platforms


class Title(Base):
    __tablename__ = "titles"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False
    )

    description: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True
    )

    title_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    release_year: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    genres = relationship(
        "Genre",
        secondary=title_genres,
        back_populates="titles"
    )

    platforms = relationship(
        "Platform",
        secondary=title_platforms,
        back_populates="titles"
    )
