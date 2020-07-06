from datetime import datetime

from .base import Base
from .. import db
from .user import User
from .group import Group


class UserGroupAssociation(Base):
    """
    User group association model
    """
    __tablename__ = "user_group_associations"
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'), primary_key=True)
    user = db.relationship("User", back_populates="associated_groups")
    group = db.relationship("Group", back_populates="associated_users")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now(), onupdate=datetime.now())

    def __init__(self,
                 user: User,
                 group: Group,
                 created_at: datetime = datetime.now(),
                 updated_at: datetime = datetime.now(),
                 **kwargs):
        super().__init__(created_at, updated_at)
        self.user = user
        self.group = group
