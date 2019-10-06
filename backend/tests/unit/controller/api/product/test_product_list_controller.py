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
        "id_list": ["id1", "id2"]
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


def test_product_list_controller(mocker, login_disabled_app, request_json, product_response_json):
    mock_product = MagicMock()
    mock_product.get_dict_min.return_value = product_response_json
    with mocker.patch.object(ProductService, "select_by_id_list", return_value=[mock_product]):
        with login_disabled_app.test_client() as client:
            response = client.post(
                "api/product/list",
                json=request_json
            )

        data = json.loads(response.data)
        SearchProductsResultsSchema().load(data)
        assert response.status_code == 200
        assert len(data["products"]) == 1


def test_product_list_controller_invalid_json(mocker, login_disabled_app, request_json):
    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/list"
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/list",
            json="notjson"
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    invalid_list = deepcopy(request_json)
    invalid_list.update(id_list="id1")

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/list",
            json=invalid_list
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400

    empty_list = deepcopy(request_json)
    empty_list.update(id_list=[])

    with login_disabled_app.test_client() as client:
        response = client.post(
            "api/product/list",
            json=empty_list
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400


@pytest.mark.parametrize(
    "method,http_method,test_url,error,status_code",
    [
        ("select_by_id_list", "POST", "/api/product/list", NoContentError(), 204),
        ("select_by_id_list", "POST", "/api/product/list", ElasticsearchException(), 504),
        ("select_by_id_list", "POST", "/api/product/list", ElasticsearchDslException(), 504),
        ("select_by_id_list", "POST", "/api/product/list", Exception(), 500)
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
