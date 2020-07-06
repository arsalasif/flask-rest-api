from __future__ import annotations
from datetime import datetime
import json
from typing import Type

from .. import db


class Base(db.Model):
    """
    Base model
    """
    __abstract__ = True
    __tablename__ = "base"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __init__(self,
                 created_at: datetime = datetime.now(),
                 updated_at: datetime = datetime.now()):
        self.created_at = created_at
        self.updated_at = updated_at

    @classmethod
    def first_by(cls, **kwargs) -> Base:
        """
        Get first entity that matches to criterion
        """
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def first(cls, *criterion) -> Base:
        """
        Get first entity that matches to criterion
        """
        return cls.query.filter(*criterion).first()

    @classmethod
    def exists(cls, *criterion) -> bool:
        """
        Check if entry with criterion exists
        """
        return cls.query.filter(*criterion).scalar()

    @classmethod
    def get(cls, _id: int) -> Base:
        """
        Get the entity that matches the id
        """
        return cls.query.get(_id)

    # This must be overridden by derived classes
    def json(self) -> json:
        """
        Get model data in JSON format
        """
        return {
            'id': self.id,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }