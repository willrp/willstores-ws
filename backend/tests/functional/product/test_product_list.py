import pytest
import requests
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory
from backend.util.response.search_products_results import SearchProductsResultsSchema
from backend.util.response.error import ErrorSchema


def test_product_list(domain_url, es_object, token_session):
    prod_list = ProductFactory.create_batch(2)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    prod_id_list = [p.meta["id"] for p in prod_list]

    response = token_session.post(
        domain_url + "/api/product/list",
        json={
            "id_list": prod_id_list,
        }
    )

    data = response.json()
    SearchProductsResultsSchema().load(data)
    assert response.status_code == 200
    assert len(data["products"]) == 2

    response = token_session.post(
        domain_url + "/api/product/list",
        json={
            "id_list": [str(uuid4()) for i in range(2)]
        }
    )

    with pytest.raises(JSONDecodeError):
        response.json()

    assert response.status_code == 204


def test_product_list_unauthorized(domain_url):
    response = requests.post(
        domain_url + "/api/product/list",
    )

    data = response.json()
    ErrorSchema().load(data)
    assert response.status_code == 401
