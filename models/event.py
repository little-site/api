from helpers.db import db
from models.base import Base
from models.user import User


class Event(Base):
    """
    Event class
    """

    __tablename__ = "events"

    user_id = db.Column(db.ForeignKey(User.id))
    type = db.Column(db.String, nullable=False)
    resource = db.Column(db.String)

    def __repr__(self):
        return "<Event {} {}>".format(self.type, self.email)
