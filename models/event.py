from helpers.db import db
from models.base import Base
from models.user import User
from user_agents import parse
from flask import request


class Event(Base):
    """
    Event class
    """

    __tablename__ = "events"

    user_id = db.Column(db.ForeignKey(User.id))
    type = db.Column(db.String, nullable=False)
    resource = db.Column(db.String)

    device_family = db.Column(db.String)
    device_model = db.Column(db.String)
    os_family = db.Column(db.String)
    os_version = db.Column(db.String)
    browser_family = db.Column(db.String)
    browser_version = db.Column(db.String)
    is_mobile = db.Column(db.Boolean)
    
    ip_address = db.Column(db.String)

    def set_agent_props(self):
        agent_props = parse(request.headers.get('User-Agent'))
        self.device_family = agent_props.device.family
        self.device_model = agent_props.device.model
        self.os_family = agent_props.os.family
        self.os_version = agent_props.os.version
        self.browser_family = agent_props.browser.family
        self.browser_version = agent_props.browser.version
        self.is_mobile = agent_props.is_mobile

    def set_ip_address(self):
        r_addr = request.remote_addr
        client_ip = request.headers.get("X-Forwarded-For", r_addr)
        self.ip_address = client_ip

    def __repr__(self):
        return "<Event {} {}>".format(self.type, self.email)
