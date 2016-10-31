from user_api import jwt


def encode_token(identity):
    return jwt.jwt_encode_callback(identity).decode('utf-8')
