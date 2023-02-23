"""Alchemy database."""
from typing import Type

from sqlalchemy.ext.declarative import AbstractConcreteBase, declarative_base

Base: Type[AbstractConcreteBase] = declarative_base()
