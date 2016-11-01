import json
import pytest

from user_api.models import User
from user_api.auth import (
    generate_auth_response,
    authenticate,
    load_identity
)


@pytest.fixture
def token():
    return 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.' + \
        'eyJleHAiOjE0Nzc5MzY3NDYsImlkZW50aXR5IjoyLCJuYmYiOjE0Nzc5MzY0NDYsImlhdCI6MTQ3NzkzNjQ0Nn0' + \
        '.zGMQyhJ25B7zHu9QoU_p2SlbfgDr0yRkTs_dQfpq6Q8'


@pytest.fixture
def user(session):
    params = {"name": "Johnny Doe",
              "email": "johnny_doe@email.com"}
    instance = User(**params)
    instance.hash_password('farofa')
    session.add(instance)
    session.flush()
    return instance


def test_authenticate_valid_credentials(user):
    response = authenticate(user.email, 'farofa')
    assert response == user


def test_authenticate_invalid_credentials(user):
    response = authenticate(user.email, 'aaa')
    assert response is None


def test_load_identity_existing_user(api_test_client, user):
    with api_test_client.application.test_request_context():
        response = load_identity({"identity": user.id})
        assert response == user


def test_load_identity_inexistent_user(api_test_client):
    with api_test_client.application.test_request_context():
        response = load_identity({"identity": 0})
        assert response is None


def test_generate_auth_response(token, user):
    response = generate_auth_response(token, user)
    data = json.loads(response)
    assert user.token == token
    assert user.token == data['token']
    for key in ['created', 'email', 'id', 'last_login', 'name', 'phones', 'token']:
        assert data[key] is not None
