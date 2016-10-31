from datetime import datetime

from flask import (
    current_app,
    jsonify
)
from jwt import encode
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError
)
from user_api.models import User
from user_api import db
from user_api.resources.schemas import UserSchema


def generate_jwt_headers(identity):
    return None


def generate_jwt_payload(identity):
    iat = datetime.utcnow()
    exp = iat + current_app.config.get('JWT_EXPIRATION_DELTA')
    nbf = iat + current_app.config.get('JWT_NOT_BEFORE_DELTA')
    identity = getattr(identity, 'id') or identity['id']
    return {'exp': exp, 'iat': iat, 'nbf': nbf, 'identity': identity}


def generate_jwt_token(identity):
    secret = current_app.config['JWT_SECRET_KEY']
    algorithm = current_app.config['JWT_ALGORITHM']
    required_claims = current_app.config['JWT_REQUIRED_CLAIMS']

    payload = generate_jwt_payload(identity)
    missing_claims = list(set(required_claims) - set(payload.keys()))

    if missing_claims:
        raise RuntimeError('Payload is missing required claims: %s' % ', '.join(missing_claims))

    headers = None
    return encode(payload, secret, algorithm=algorithm, headers=headers)


def generate_auth_response(access_token, identity):
    try:
        user = User.query.get(identity.id)
        user.token = access_token
        user.last_login_at = datetime.utcnow()
        db.session.add(user)
        db.session.commit()
        return UserSchema().dumps(user).data
    except IntegrityError as e:
        current_app.logger.error(e)


def authenticate(email, password):
    user = User.query.filter_by(email=email).first()
    if user and user.verify_password(password):
        return user


def load_identity(payload):
    user_id = payload['identity']
    try:
        user = User.query.filter_by(id=user_id).one()
        return user
    except SQLAlchemyError:
        current_app.logger.error('User with id {} not found'.format(user_id))


def generate_error_response(err):
    ERRORS = {'Bad Request': 'Usuário e/ou senha inválidos',
              'Invalid JWT header': 'Token inválido',
              'Authorization Required': 'Token não enviado',
              'Invalid token': 'Token inválido',
              'Invalid JWT': 'Usuário não encontrado'}
    message = ERRORS.get(err.error) or err.error
    return jsonify({"mensagem": message}), err.status_code
