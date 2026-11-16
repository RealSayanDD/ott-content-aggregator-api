
from sqlalchemy import Table, Column, ForeignKey
from src.models.base import Base


# Connect titles with genres
title_genres = Table(
    "title_genres",
    Base.metadata,

    Column(
        "title_id",
        ForeignKey("titles.id"),
        primary_key=True
    ),

    Column(
        "genre_id",
        ForeignKey("genres.id"),
        primary_key=True
    )
)


# Connect titles with OTT platforms
title_platforms = Table(
    "title_platforms",
    Base.metadata,

    Column(
        "title_id",
        ForeignKey("titles.id"),
        primary_key=True
    ),

    Column(
        "platform_id",
        ForeignKey("platforms.id"),
        primary_key=True
    )
)
