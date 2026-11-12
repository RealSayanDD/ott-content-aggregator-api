
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Shared declarative base for all database models.

    Title, Genre, Platform, User, and other models
    should inherit from this class.
    """
    pass
