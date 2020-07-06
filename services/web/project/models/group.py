from __future__ import annotations
from datetime import datetime
from sqlalchemy.ext.associationproxy import association_proxy

from .base import Base
from .. import db

class Group(Base):
    """
    Group user can be a part of
    """
    __tablename__ = "group"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(128))
    associated_users = db.relationship("UserGroupAssociation", back_populates="group")
    users = association_proxy('associated_users', 'user')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self,
                 name: str,
                 created_at: datetime = datetime.now(),
                 updated_at: datetime = datetime.now(),
                 **kwargs):
        super().__init__(created_at, updated_at)
        self.name = name