from flask import jsonify
from sqlalchemy.exc import (
    SQLAlchemyError,
    IntegrityError
)
from webargs.core import ValidationError
from flask_jwt import JWT

from user_api.resources.user import UserResource
from user_api import (
    user_api_app as app,
    api,
    db
)
from user_api.auth import (
    generate_jwt_token,
    generate_jwt_payload,
    generate_jwt_headers,
    generate_auth_response,
    generate_error_response,
    authenticate,
    load_identity
)


api.add_resource(UserResource, "/users")


jwt = JWT(app, authenticate, load_identity)
jwt.jwt_encode_callback = generate_jwt_token
jwt.jwt_payload_callback = generate_jwt_payload
jwt.jwt_headers_callback = generate_jwt_headers
jwt.auth_response_callback = generate_auth_response
jwt.jwt_error_callback = generate_error_response


@app.route("/healthcheck")
def healthcheck():
    try:
        db.engine.execute("SELECT 1;").fetchone()
        return jsonify({"status": "OK"})
    except SQLAlchemyError:
        return jsonify({"status": "DOWN"})


@app.errorhandler(404)
def handle_not_found(err):
    return jsonify({"mensagem": 'Resource not found'}), 404


@app.errorhandler(IntegrityError)
def handle_integrity_error(err):
    return jsonify({"messagem": str(err)}), 422


@app.errorhandler(ValidationError)
def handle_unprocessable_entity(err):
    messages = ["{} {}".format(key, ",".join(value)) for key, value in err.messages.items()]
    return jsonify({"mensagem": "; ".join(messages)}), 400


if __name__ == "__main__":
    app.run()
