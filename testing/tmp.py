from pytest_fixture_forms import FixtureForms
import pytest


class UserCredentials(FixtureForms):
    @pytest.fixture
    def valid_user(self):
        return {"username": "john_doe", "password": "secure123"}

    @pytest.fixture
    def invalid_password(self):
        return {"username": "john_doe", "password": "wrong"}

    @pytest.fixture
    def missing_username(self):
        return {"username": "", "password": "secure123"}


def test_login(user_credentials):
    # This test will run for each form defined in UserCredentials
    response = login_service.authenticate(**user_credentials.value)

    if user_credentials.form == "valid_user":
        assert response.status_code == 200
    else:
        assert response.status_code == 401
