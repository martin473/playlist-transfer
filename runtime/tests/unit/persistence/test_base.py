"""Unit tests for the declarative base."""

import importlib

import pytest
from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase

from playlist_bridge.persistence import Base


class TestDeclarativeBase:
    """Test suite for the Base declarative base class."""

    def test_base_is_declarative_base_subclass(self) -> None:
        """Verify that Base inherits from SQLAlchemy's DeclarativeBase."""
        assert issubclass(Base, DeclarativeBase)
        assert isinstance(Base, type)

    def test_base_has_metadata_attribute(self) -> None:
        """Verify that Base has a metadata attribute of type MetaData."""
        assert hasattr(Base, "metadata")
        assert isinstance(Base.metadata, MetaData)

    def test_base_metadata_is_isolated(self) -> None:
        """Verify that Base.metadata is distinct and can be used for schema."""
        # The metadata should be empty initially (no models registered yet).
        assert len(Base.metadata.tables) == 0

    def test_import_exposes_exactly_one_base_from_package(self) -> None:
        """Acceptance: Importing the persistence package exposes exactly one base metadata object."""
        # Reload the persistence module to ensure fresh import
        persistence_module = importlib.import_module("playlist_bridge.persistence")
        
        # Collect all attributes that are instances of DeclarativeBase
        base_classes = [
            getattr(persistence_module, name)
            for name in dir(persistence_module)
            if isinstance(getattr(persistence_module, name), type)
            and issubclass(getattr(persistence_module, name), DeclarativeBase)
            and getattr(persistence_module, name) is not DeclarativeBase
        ]
        
        # Exactly one Base class should be exposed
        assert len(base_classes) == 1, f"Expected exactly one declarative base, found {len(base_classes)}"
        assert base_classes[0] is Base

    def test_base_is_usable_for_model_definition(self) -> None:
        """Verify that Base can be used as a base for defining models."""
        from sqlalchemy import Column, Integer, String
        from sqlalchemy.orm import Mapped, mapped_column

        class SampleModel(Base):
            __tablename__ = "sample"
            id: Mapped[int] = mapped_column(Integer, primary_key=True)
            name: Mapped[str] = mapped_column(String(50))

        # The model should be registered in Base.metadata
        assert "sample" in Base.metadata.tables
        table = Base.metadata.tables["sample"]
        assert "id" in table.columns
        assert "name" in table.columns

        # Clean up: remove the table from metadata to keep tests isolated
        Base.metadata.remove(table)
