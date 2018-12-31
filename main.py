import os
from flask import Flask
from flask_restful import Api as API
from flask_cors import CORS
from helpers.db import db

from routes import route_dict

# MARK - Setup Flask app
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["SQLALCHEMY_DATABASE_URI"]
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)

# Set up SQLAlchemy
db.init_app(app)

# Set up Flask-Restful API wrapper
api = API(app)

# MARK - Add routes from /routes/__init__.py
for route, resource in route_dict.items():
    api.add_resource(resource, route)

if __name__ == "__main__":
    # TODO: Make this an ENV var
    app.run()