import pytest
from flask import json
from elasticsearch import ElasticsearchException
from elasticsearch_dsl.exceptions import ElasticsearchDslException

from backend.service import ProductService
from backend.util.response.products_count import ProductsCountSchema
from backend.util.response.error import ErrorSchema


@pytest.fixture(scope="function", autouse=True)
def controller_mocker(mocker):
    mocker.patch.object(ProductService, "__init__", return_value=None)


def test_start_controller(mocker, login_disabled_app):
    with mocker.patch.object(ProductService, "products_count", return_value=5):
        with login_disabled_app.test_client() as client:
            response = client.get(
                "api/start"
            )

        data = json.loads(response.data)
        ProductsCountSchema().load(data)

        assert response.status_code == 200


@pytest.mark.parametrize(
    "method,http_method,test_url,error,status_code",
    [
        ("products_count", "GET", "/api/start", ElasticsearchException(), 504),
        ("products_count", "GET", "/api/start", ElasticsearchDslException(), 504),
        ("products_count", "GET", "/api/start", Exception(), 500)
    ]
)
def test_start_controller_error(mocker, get_request_function, method, http_method, test_url, error, status_code):
    with mocker.patch.object(ProductService, method, side_effect=error):
        make_request = get_request_function(http_method)

        response = make_request(
            test_url
        )

        data = json.loads(response.data)
        ErrorSchema().load(data)

        assert response.status_code == status_code
