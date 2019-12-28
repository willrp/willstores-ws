import pytest
from flask import json
from unittest.mock import MagicMock
from copy import deepcopy
from elasticsearch import ElasticsearchException
from elasticsearch_dsl.exceptions import ElasticsearchDslException
from json.decoder import JSONDecodeError

from backend.service import ProductService, SessionService
from backend.util.response.session_results import SessionResultsSchema
from backend.util.response.error import ErrorSchema
from backend.errors.no_content_error import NoContentError
from backend.errors.not_found_error import NotFoundError


@pytest.fixture(scope="module")
def request_json():
    return {
        "pricerange": {
            "min": 1000,
            "max": 2000
        }
    }


@pytest.fixture(scope="module")
def pricerange_response_json():
    return {
        "min": 10,
        "max": 20
    }


@pytest.fixture(scope="module")
def sessions_response_json():
    return [
        {
            "id": "string",
            "name": "string",
            "gender": "string",
            "image": "string",
            "total": 100
        }
    ]


@pytest.fixture(scope="module")
def brands_response_json():
    return [
        {
            "brand": "string",
            "amount": 10
        }
    ]


@pytest.fixture(scope="module")
def kinds_response_json():
    return [
        {
            "kind": "string",
            "amount": 10
        }
    ]


@pytest.fixture(scope="function", autouse=True)
def controller_mocker(mocker):
    mocker.patch.object(ProductService, "__init__", return_value=None)
    mocker.patch.object(SessionService, "__init__", return_value=None)


def test_session_controller(mocker, login_disabled_app, request_json, sessions_response_json, brands_response_json, kinds_response_json, pricerange_response_json):
    with mocker.patch.object(SessionService, "select_by_id", return_value=MagicMock(gender="test")):
        with mocker.patch.object(SessionService, "select", return_value=sessions_response_json):
            with mocker.patch.object(ProductService, "get_total", return_value=10):
                with mocker.patch.object(ProductService, "select_brands", return_value=brands_response_json):
                    with mocker.patch.object(ProductService, "select_kinds", return_value=kinds_response_json):
                        with mocker.patch.object(ProductService, "select_pricerange", return_value=pricerange_response_json):
                            with login_disabled_app.test_client() as client:
                                response = client.post(
                                    "api/session/test"
                                )

                            data = json.loads(response.data)
                            SessionResultsSchema().load(data)
                            assert response.status_code == 200
                            assert data["total"] == 10
                            assert data["pricerange"] == pricerange_response_json

                            with login_disabled_app.test_client() as client:
                                response = client.post(
                                    "api/session/test",
                                    json=request_json
                                )

                            data = json.loads(response.data)
                            SessionResultsSchema().load(data)
                            assert response.status_code == 200
                            assert data["total"] == 10
                            assert data["pricerange"] == pricerange_response_json


def test_session_controller_invalid_json(mocker, login_disabled_app, request_json):
    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/session/test",
            json="notjson"
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_min = deepcopy(request_json)
    invalid_min["pricerange"].update(min=-10.0)

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/session/test",
            json=invalid_min
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_max = deepcopy(request_json)
    invalid_max["pricerange"].update(max=-10.0)

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/session/test",
            json=invalid_max
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_range = deepcopy(request_json)
    invalid_range["pricerange"].update(min=100.0, max=50.0)

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/session/test",
            json=invalid_range
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400


@pytest.mark.parametrize(
    "method,http_method,test_url,error,status_code",
    [
        ("select_by_id", "POST", "/api/session/test", NoContentError(), 204),
        ("select_by_id", "POST", "/api/session/test", NotFoundError(), 404),
        ("select_by_id", "POST", "/api/session/test", ElasticsearchException(), 504),
        ("select_by_id", "POST", "/api/session/test", ElasticsearchDslException(), 504),
        ("select_by_id", "POST", "/api/session/test", Exception(), 500)
    ]
)
def test_start_controller_error(mocker, get_request_function, method, http_method, test_url, error, status_code):
    with mocker.patch.object(SessionService, method, side_effect=error):
        make_request = get_request_function(http_method)

        response = make_request(
            test_url
        )

        if status_code == 204:
            with pytest.raises(JSONDecodeError):
                json.loads(response.data)
        else:
            data = json.loads(response.data)
            if status_code == 404:
                assert data == {}
            else:
                ErrorSchema().load(data)

        assert response.status_code == status_code
