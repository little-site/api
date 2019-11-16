from flask_restful import Resource
from models.event import Event
from models.user import User
from helpers.auth import security
from helpers.io import json_input

VALID_PUB_EVENTS = [
    "view"
]

VALID_PRIV_EVENTS = VALID_PUB_EVENTS + [
    "sign in",
    "sign out",
    "check in"
]

ALLOWED_EVENT_FIELDS = [
    "type",
    "resource"
]

NEED_EVENT_TYPE = "You must include a valid event 'type'"
INVALID_EVENT_TYPE = "Sorry, that event 'type' is invalid"


class EventsEndpoint(Resource):
    """
    Route used for creating events, either from a user or public events
    """

    @security()
    @json_input(ALLOWED_EVENT_FIELDS)
    def post(self, fields, authorized, **kwargs):
        """
        Route for creating an event
        """

        if "type" not in fields:
            return {"message": NEED_EVENT_TYPE}, 400

        event = Event(**fields)

        valid_types = VALID_PUB_EVENTS

        if authorized:
            valid_types = VALID_PRIV_EVENTS
            event.user_id = kwargs["user"].id

        if not fields["type"] in valid_types:
            return {"message": INVALID_EVENT_TYPE}, 400

        event.save()

        return event.to_dict(), 201
