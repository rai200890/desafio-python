
from flask import jsonify
from flask_jwt import JWT

from user_api import app, db
from user_api.models import User


def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and user.verify_password(password):
        return user


def identity_loader(payload):
    user_id = payload['identity']
    try:
        user = User.query.filter_by(id=user_id).one()
        return user
    except Exception as e:
        app.logger.error(e)


jwt = JWT(app, authenticate, identity_loader)


@app.route("/healthcheck")
def healthcheck():
    result = db.engine.execute("SELECT 1;").fetchone()
    return "DB: OK {}".format(result)


@app.errorhandler(404)
def handle_not_found(err):
    return jsonify({"errors": 'Resource not found'}), 404


if __name__ == "__main__":
    app.run()
