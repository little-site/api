from helpers.auth import security
from helpers.db import db
from helpers.io import json_input
from helpers.apple import retrieve_user
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.user import User
from models.token import AuthToken
from models.site import Site
import os


class AuthEndpoint(Resource):
    """
    Routes defined for signing in users
    """
    @security(True)
    def get(self, user, token, **kwargs):
        """Base auth test endpoint that will retrieve  a user given a token"""
        # If you get this far in endpoints that have @security(True)
        # Then a Token and a User exist in the kwargs
        site = Site.query.filter_by(user_id=user.id).first()

        return {
            "user": user.to_dict(),
            "token": token.to_dict(),
            "site": site.to_dict()
        }, 200
    
    @json_input(["apple_token", "given_name", "family_name", "name"])
    def post(self, fields, **kwargs):
        """
        This endpoint signs in users with an apple_token field.

        Apple tokens sometimes contain emails (when it's a new user) and otherwise don't
        "sub" is Apple's user PK
        Name is passed to if it's available and should be treated as optional
        
        If the user's email exists, the existing user object will be returned
        If the user's email does not exist, a new User will be saved
        
        Either way, a new token will be issued
        """

        try:
            # Validate the apple_token passed in (retrieves apple user)
            apple_user = retrieve_user(fields["apple_token"])
        except Exception as e:
            # Handle exceptions
            return {
                "message": str(e)
            }, 400

        is_new_user = True
        
        if apple_user.full_user:
            # Make a new User
            user = User(
                email=apple_user.email,
                name=fields["name"],
                apple_id=apple_user.id
            )

            try:
                # Save the new user to the DB
                user.save()

            except IntegrityError:
                # That user already exists, rollback
                is_new_user = False
                db.session().rollback()

                # Find existing user
                user = User.query.filter_by(apple_id=apple_user.id).first()
                pass
        else:
            is_new_user = False
            user = User.query.filter_by(apple_id=apple_user.id).first()

        # # Mark previous tokens expired
        # TODO: This will expire shortcuts tokens which is bad
        # db.session.query(AuthToken).filter_by(
        #     user_id=user.id).update({AuthToken.expired: True})
        # db.session.commit()

        # Send back a new auth token
        new_token = AuthToken(user_id=user.id)
        new_token.save()

        return_payload = {
            "user": user.to_dict(),
            "token": new_token.to_dict()
        }
        status_code = 200

        # Create a user's first site
        if is_new_user:
            status_code = 201
            new_site = Site(user_id=user.id)
            new_site.set_first_handle(user.name)
            return_payload["site"] = new_site.to_dict()
        else:
            # Look up existing site
            site = Site.query.filter_by(user_id=user.id).first()
            return_payload["site"] = site.to_dict()

        return return_payload, status_code
