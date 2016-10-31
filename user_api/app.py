from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from webargs.core import ValidationError

from user_api.resources.user import UserResource
from user_api import (
    user_api_app as app,
    api,
    db
)


api.add_resource(UserResource, "/users")


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
