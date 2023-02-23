"""Base classes for database models."""
from __future__ import annotations

import typing as t

from pydantic import BaseModel
from sqlalchemy import Column, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import Base

# БОЛЬШЕ ДЖЕНЕРИКОВ БОГУ ДЖЕНЕРИКОВ
T = t.TypeVar("T", bound="AbstractModel")


class AbstractModel(Base):
    """Base database model.

    It provides the basic methods like save, remove, update, etc.
    for all the models.

    Models with one primary key are supported.
    """

    # https://docs.sqlalchemy.org/en/20/changelog/migration_20.html#migration-to-2-0-step-six-add-allow-unmapped-to-explicitly-typed-orm-models
    __allow_unmapped__ = True
    __abstract__ = True

    def __repr__(self) -> str:
        """Return the representation of the model."""
        return f"<{self.__class__.__name__} {self.get_primary_key()}={self.get_primary_key_value(self)}>"

    def __str__(self) -> str:
        """Return the string representation of the model."""
        return self.__repr__()

    def __eq__(self, other: t.Any) -> bool:
        """Check if the model is equal to another object."""
        if not isinstance(other, AbstractModel):
            return False
        return self.get_primary_key_value(self) == other.get_primary_key_value(other)

    def __ne__(self, other: t.Any) -> bool:
        """Check if the model is not equal to another object."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Return the hash of the model."""
        return hash(self.get_primary_key_value(self))

    def to_dict(self) -> dict[str, t.Any]:
        """Return the dictionary representation of the model."""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}  # type: ignore

    @classmethod
    def from_dict(cls: t.Type[T], data: dict[str, t.Any]) -> T:
        """Create a model from a dictionary."""
        return cls(**data)

    @classmethod
    def from_schema(cls: t.Type[T], model: BaseModel) -> T:
        """Create a model from pydantic schema."""
        return cls.from_dict(model.dict())

    @classmethod
    def get_primary_key(cls) -> str:
        """Return the primary key of the model."""
        return cls.__table__.primary_key.columns.values()[0].name  # type: ignore

    @classmethod
    def get_primary_key_value(cls: t.Type[T], model: T) -> t.Any:
        """Return the primary key value of the model."""
        return getattr(model, cls.get_primary_key())

    @classmethod
    async def get(cls: t.Type[T], db: AsyncSession, primary_key: t.Any) -> T | None:
        """Get a model by primary key."""
        query = select(cls).filter_by(**{cls.get_primary_key(): primary_key})
        return (await db.execute(query)).scalars().first()

    @staticmethod
    def _get_column(model: t.Type[T], column: Column[t.Any]) -> str:
        """Get a column name."""
        name = column.name
        if name not in model.__table__.columns:  # type: ignore
            raise ValueError(f"Column {name} not found in {model.__name__}")
        return name

    @classmethod
    async def get_by_key(
        cls: t.Type[T], db: AsyncSession, key: Column[t.Any], value: t.Any
    ) -> T | None:
        """Get a model by a key."""
        query = select(cls).filter_by(**{cls._get_column(cls, key): value})
        return (await db.execute(query)).scalars().first()

    @classmethod
    async def get_list_by_key(
        cls: t.Type[T],
        db: AsyncSession,
        key: Column[t.Any],
        value: t.Any,
        limit: int = 10,
        offset: int = 0,
    ) -> t.Sequence[T]:
        """Get a list of models by a key."""
        query = (
            select(cls)
            .filter_by(**{cls._get_column(cls, key): value})
            .offset(offset)
            .limit(limit)
        )
        return (await db.execute(query)).scalars().all()

    @classmethod
    async def get_by_keys(
        cls: t.Type[T], db: AsyncSession, /, **kwargs: t.Any
    ) -> T | None:
        """Get a model by multiple keys."""
        query = select(cls).filter_by(**kwargs)
        return (await db.execute(query)).scalars().first()

    @classmethod
    async def get_list_by_keys(
        cls: t.Type[T],
        db: AsyncSession,
        *,
        limit: int = 0,
        offset: int = 0,
        **kwargs: t.Any,
    ) -> t.Sequence[T]:
        """Get a list of models by multiple keys."""
        query = select(cls).filter_by(**kwargs).offset(offset).limit(limit)
        return (await db.execute(query)).scalars().all()

    @classmethod
    async def create(cls: t.Type[T], db: AsyncSession, **kwargs: t.Any) -> T:
        """Create a new model."""
        model = cls(**kwargs)
        await model.save(db)
        return model

    @classmethod
    async def remove_by_primary(
        cls: t.Type[T], db: AsyncSession, primary_key: t.Any
    ) -> None:
        """Remove a model by primary key."""
        model = await cls.get(db, primary_key)
        if model:
            await model.remove(db)

    async def remove(self, db: AsyncSession) -> None:
        """Remove the model."""
        await db.delete(self)
        await db.flush()

    async def save(self, db: AsyncSession) -> None:
        """Save the model."""
        db.add(self)
        await db.flush()

    async def update(self, db: AsyncSession, **kwargs: t.Any) -> None:
        """Update the model."""
        for key, value in kwargs.items():
            setattr(self, key, value)
        await self.save(db)
