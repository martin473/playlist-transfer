"""Declarative base for SQLAlchemy ORM models."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Base class for all playlist-bridge ORM models.

    All model classes should inherit from this base, which provides
    the SQLAlchemy declarative mapping foundation and metadata registry.
    """

    # No additional configuration is required; DeclarativeBase handles
    # metadata collection and registry setup automatically.
    pass
