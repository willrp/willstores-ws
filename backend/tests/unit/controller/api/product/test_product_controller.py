import pytest
from flask import json
from unittest.mock import MagicMock
from elasticsearch import ElasticsearchException
from elasticsearch_dsl.exceptions import ElasticsearchDslException

from backend.service import ProductService
from backend.util.response.product_results import ProductResultsSchema
from backend.util.response.error import ErrorSchema
from backend.errors.not_found_error import NotFoundError


@pytest.fixture(scope="module")
def response_json():
    return {
        "id": "string",
        "name": "string",
        "kind": "string",
        "brand": "string",
        "details": [
            "string"
        ],
        "care": "string",
        "about": "string",
        "images": [
            "string"
        ],
        "gender": "string",
        "price": {
            "outlet": 10.55,
            "retail": 20.9,
            "symbol": "£"
        }
    }


@pytest.fixture(scope="function", autouse=True)
def controller_mocker(mocker):
    mocker.patch.object(ProductService, "__init__", return_value=None)


def test_product_controller(mocker, login_disabled_app, response_json):
    mock_product = MagicMock()
    mock_product.get_dict.return_value = response_json
    with mocker.patch.object(ProductService, "select_by_id", return_value=mock_product):
        with login_disabled_app.test_client() as client:
            response = client.get(
                "api/product/id"
            )

        data = json.loads(response.data)
        ProductResultsSchema().load(data)
        assert response.status_code == 200


@pytest.mark.parametrize(
    "method,http_method,test_url,error,status_code",
    [
        ("select_by_id", "GET", "api/product/id", NotFoundError(), 404),
        ("select_by_id", "GET", "api/product/id", ElasticsearchException(), 504),
        ("select_by_id", "GET", "api/product/id", ElasticsearchDslException(), 504),
        ("select_by_id", "GET", "api/product/id", Exception(), 500)
    ]
)
def test_product_controller_error(mocker, get_request_function, method, http_method, test_url, error, status_code):
    with mocker.patch.object(ProductService, method, side_effect=error):
        make_request = get_request_function(http_method)

        response = make_request(
            test_url
        )

        data = json.loads(response.data)

        if status_code == 404:
            assert data == {}
        else:
            ErrorSchema().load(data)

        assert response.status_code == status_code
