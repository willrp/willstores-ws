import pytest

from backend import create_app


@pytest.fixture(scope="session")
def login_disabled_app(flask_app):
    test_app = create_app(flask_env="test")
    test_app.config = flask_app.config
    test_app.config["LOGIN_DISABLED"] = True
    yield test_app


@pytest.fixture(scope="session")
def get_request_function(login_disabled_app):
    def decision_function(http_method):
        if http_method == "GET":
            return login_disabled_app.test_client().get
        else:
            return login_disabled_app.test_client().post

    return decision_function
