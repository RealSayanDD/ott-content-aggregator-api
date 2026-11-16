
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.models.base import Base
from src.models.association import title_platforms


class Platform(Base):
    __tablename__ = "platforms"

    id: Mapped[int] = mapped_column(
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    website: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    titles = relationship(
        "Title",
        secondary=title_platforms,
        back_populates="platforms"
    )
