import pytest
from flask import json
from unittest.mock import MagicMock
from copy import deepcopy
from elasticsearch import ElasticsearchException
from elasticsearch_dsl.exceptions import ElasticsearchDslException
from json.decoder import JSONDecodeError

from backend.service import ProductService, SessionService
from backend.util.response.gender_results import GenderResultsSchema
from backend.util.response.error import ErrorSchema
from backend.errors.no_content_error import NoContentError


@pytest.fixture(scope="module")
def request_json():
    return {
        "amount": "5"
    }


@pytest.fixture(scope="module")
def discount_response_json():
    return {
        "id": "string",
        "name": "string",
        "image": "string",
        "price": {
            "outlet": 10.55,
            "retail": 20.9,
            "symbol": "£"
        },
        "discount": 80.5
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


def test_gender_controller(mocker, login_disabled_app, request_json, discount_response_json, sessions_response_json, brands_response_json, kinds_response_json):
    mock_discount = MagicMock()
    mock_discount.get_dict_min.return_value = discount_response_json
    with mocker.patch.object(ProductService, "super_discounts", return_value=[mock_discount]):
        with mocker.patch.object(SessionService, "select", return_value=sessions_response_json):
            with mocker.patch.object(ProductService, "select_brands", return_value=brands_response_json):
                with mocker.patch.object(ProductService, "select_kinds", return_value=kinds_response_json):
                    with login_disabled_app.test_client() as client:
                        response = client.post(
                            "api/gender/test"
                        )

                    data = json.loads(response.data)
                    GenderResultsSchema().load(data)
                    assert response.status_code == 200
                    assert len(data["discounts"]) == 1

                    with login_disabled_app.test_client() as client:
                        response = client.post(
                            "api/gender/test",
                            json=request_json
                        )

                    data = json.loads(response.data)
                    GenderResultsSchema().load(data)
                    assert response.status_code == 200
                    assert len(data["discounts"]) == 1


def test_gender_controller_invalid_json(mocker, login_disabled_app, request_json):
    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/gender/test",
            json="notjson"
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_amount = deepcopy(request_json)
    invalid_amount.update(amount=0)

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/gender/test",
            json=invalid_amount
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400


@pytest.mark.parametrize(
    "method,http_method,test_url,error,status_code",
    [
        ("super_discounts", "POST", "/api/gender/test", NoContentError(), 204),
        ("super_discounts", "POST", "/api/gender/test", ElasticsearchException(), 504),
        ("super_discounts", "POST", "/api/gender/test", ElasticsearchDslException(), 504),
        ("super_discounts", "POST", "/api/gender/test", Exception(), 500)
    ]
)
def test_gender_controller_error(mocker, get_request_function, method, http_method, test_url, error, status_code):
    with mocker.patch.object(ProductService, method, side_effect=error):
        make_request = get_request_function(http_method)

        response = make_request(
            test_url
        )

        if status_code == 204:
            with pytest.raises(JSONDecodeError):
                json.loads(response.data)
        else:
            data = json.loads(response.data)
            ErrorSchema().load(data)

        assert response.status_code == status_code
