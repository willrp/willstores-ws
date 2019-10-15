import pytest
from flask import json
from unittest.mock import MagicMock
from copy import deepcopy
from elasticsearch import ElasticsearchException
from elasticsearch_dsl.exceptions import ElasticsearchDslException
from json.decoder import JSONDecodeError

from backend.service import ProductService
from backend.util.response.products_total import ProductTotalSchema
from backend.util.response.error import ErrorSchema
from backend.errors.no_content_error import NoContentError
from backend.errors.request_error import ValidationError


@pytest.fixture(scope="module")
def request_json():
    return {
        "item_list": [
            {"item_id": "id", "amount": 2},
            {"item_id": "id", "amount": 3}
        ]
    }


@pytest.fixture(scope="module")
def product_response_json():
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


@pytest.fixture(scope="function", autouse=True)
def controller_mocker(mocker):
    mocker.patch.object(ProductService, "__init__", return_value=None)


def test_product_total_controller(mocker, login_disabled_app, request_json, product_response_json):
    mock_product = MagicMock()
    mock_product.get_dict_min.return_value = product_response_json
    with mocker.patch.object(ProductService, "select_by_item_list", return_value=([mock_product], product_response_json["price"])):
        with login_disabled_app.test_client() as client:
            response = client.post(
                "api/product/total",
                json=request_json
            )

        data = json.loads(response.data)
        ProductTotalSchema().load(data)
        assert response.status_code == 200
        assert data["total"] == product_response_json["price"]


def test_product_total_controller_invalid_json(mocker, login_disabled_app, request_json):
    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/total"
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/total",
            json="notjson"
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_list = deepcopy(request_json)
    invalid_list.update(item_list="id1")

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/total",
            json=invalid_list
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    empty_list = deepcopy(request_json)
    empty_list.update(item_list=[])

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/total",
            json=empty_list
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    no_item_id = deepcopy(request_json)
    del no_item_id["item_list"][0]["item_id"]

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/total",
            json=no_item_id
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    no_amount = deepcopy(request_json)
    del no_amount["item_list"][0]["amount"]

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/total",
            json=no_amount
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_amount = deepcopy(request_json)
    invalid_amount["item_list"][0].update(amount=0)

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/total",
            json=invalid_amount
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400


@pytest.mark.parametrize(
    "method,http_method,test_url,error,status_code",
    [
        ("select_by_item_list", "POST", "/api/product/total", NoContentError(), 204),
        ("select_by_item_list", "POST", "/api/product/total", ValidationError("test"), 400),
        ("select_by_item_list", "POST", "/api/product/total", ElasticsearchException(), 504),
        ("select_by_item_list", "POST", "/api/product/total", ElasticsearchDslException(), 504),
        ("select_by_item_list", "POST", "/api/product/total", Exception(), 500)
    ]
)
def test_kind_products_controller_error(mocker, get_request_function, request_json, method, http_method, test_url, error, status_code):
    with mocker.patch.object(ProductService, method, side_effect=error):
        make_request = get_request_function(http_method)

        response = make_request(
            test_url,
            json=request_json
        )

        if status_code == 204:
            with pytest.raises(JSONDecodeError):
                json.loads(response.data)
        else:
            data = json.loads(response.data)
            ErrorSchema().load(data)

        assert response.status_code == status_code
