from datetime import datetime

from flask import current_app, jsonify, abort
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from webargs.flaskparser import use_kwargs, FlaskParser
from marshmallow.exceptions import ValidationError

from user_api.resources.schemas import (
    UserRequestSchema,
    UserSchema
)
from user_api import db
from user_api.models import (
    User,
    Phone
)
from user_api.auth import generate_jwt_token


class UserResource(Resource):

    @use_kwargs(UserRequestSchema())
    def post(self, **kwargs):
        try:
            password = kwargs.pop('password')
            phones = kwargs.pop('phones')
            user = User(**kwargs)
            for phone in phones:
                params = phone
                params["user"] = user
                db.session.add(Phone(**params))
            user.hash_password(password)
            db.session.add(user)
            db.session.flush()
            user.token = generate_jwt_token(user).decode('utf-8')
            user.last_login_at = datetime.utcnow()
            db.session.commit()
            return UserSchema().dump(user).data
        except IntegrityError as err:
            db.session.rollback()
            current_app.logger.error(err)
            return {"messagem": 'O usuario não pode ser criado'}, 422
