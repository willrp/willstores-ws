import pytest
from flask import json
from unittest.mock import MagicMock
from copy import deepcopy
from elasticsearch import ElasticsearchException
from elasticsearch_dsl.exceptions import ElasticsearchDslException
from json.decoder import JSONDecodeError

from backend.service import ProductService
from backend.util.response.search_products_results import SearchProductsResultsSchema
from backend.util.response.error import ErrorSchema
from backend.errors.no_content_error import NoContentError


@pytest.fixture(scope="module")
def request_json():
    return {
        "pricerange": {
            "min": 1000,
            "max": 2000
        },
        "pagesize": 5
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


def test_kind_products_controller(mocker, login_disabled_app, request_json, product_response_json):
    mock_product = MagicMock()
    mock_product.get_dict_min.return_value = product_response_json
    with mocker.patch.object(ProductService, "select", return_value=[mock_product]):
        with login_disabled_app.test_client() as client:
            response = client.post(
                "api/kind/test/1"
            )

        data = json.loads(response.data)
        SearchProductsResultsSchema().load(data)
        assert response.status_code == 200
        assert len(data["products"]) == 1

        with login_disabled_app.test_client() as client:
            response = client.post(
                "api/kind/test/1",
                json=request_json
            )

        data = json.loads(response.data)
        SearchProductsResultsSchema().load(data)
        assert response.status_code == 200
        assert len(data["products"]) == 1


def test_kind_products_controller_invalid_json(mocker, login_disabled_app, request_json):
    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/kind/test/1",
            json="notjson"
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_min = deepcopy(request_json)
    invalid_min["pricerange"].update(min=-10.0)

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/kind/test/1",
            json=invalid_min
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_max = deepcopy(request_json)
    invalid_max["pricerange"].update(max=-10.0)

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/kind/test/1",
            json=invalid_max
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_range = deepcopy(request_json)
    invalid_range["pricerange"].update(min=100.0, max=50.0)

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/kind/test/1",
            json=invalid_range
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_pagesize = deepcopy(request_json)
    invalid_pagesize.update(pagesize=0)

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/kind/test/1",
            json=invalid_pagesize
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400


@pytest.mark.parametrize(
    "method,http_method,test_url,error,status_code",
    [
        ("select", "POST", "/api/kind/test/1", NoContentError(), 204),
        ("select", "POST", "/api/kind/test/1", ElasticsearchException(), 504),
        ("select", "POST", "/api/kind/test/1", ElasticsearchDslException(), 504),
        ("select", "POST", "/api/kind/test/1", Exception(), 500)
    ]
)
def test_kind_products_controller_error(mocker, get_request_function, method, http_method, test_url, error, status_code):
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
