import pytest
import requests
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory
from backend.util.response.search_results import SearchResultsSchema
from backend.util.response.error import ErrorSchema


def test_brand(domain_url, es_object, token_session):
    brand = str(uuid4())
    prod_list = ProductFactory.create_batch(2, brand=brand)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    response = token_session.post(
        domain_url + "/api/brand/%s" % brand
    )

    data = response.json()
    SearchResultsSchema().load(data)
    assert response.status_code == 200
    assert data["total"] == 2

    response = token_session.post(
        domain_url + "/api/brand/%s" % brand,
        json={
            "pricerange": {
                "min": 1,
                "max": 500
            }
        }
    )

    data = response.json()
    SearchResultsSchema().load(data)
    assert response.status_code == 200
    assert data["total"] == 2

    response = token_session.post(
        domain_url + "/api/brand/%s" % brand,
        json={
            "pricerange": {
                "min": 10000,
                "max": 20000
            }
        }
    )

    with pytest.raises(JSONDecodeError):
        response.json()

    assert response.status_code == 204

    response = token_session.post(
        domain_url + "/api/brand/%s" % str(uuid4())
    )

    with pytest.raises(JSONDecodeError):
        response.json()

    assert response.status_code == 204


def test_brand_unauthorized(domain_url):
    response = requests.post(
        domain_url + "/api/brand/1",
    )

    data = response.json()
    ErrorSchema().load(data)
    assert response.status_code == 401
