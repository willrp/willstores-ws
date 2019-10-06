import pytest
import requests
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory
from backend.util.response.search_results import SearchResultsSchema
from backend.util.response.error import ErrorSchema


def test_search(domain_url, es_object, token_session):
    query = str(uuid4())
    prod_list = [
        ProductFactory.create(name=query),
        ProductFactory.create(gender=query),
        ProductFactory.create(kind=query),
        ProductFactory.create(brand=query)
    ]
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    response = token_session.post(
        domain_url + "/api/search/%s" % query
    )

    data = response.json()
    SearchResultsSchema().load(data)
    assert response.status_code == 200
    assert data["total"] == 4

    response = token_session.post(
        domain_url + "/api/search/%s" % query,
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
    assert data["total"] == 4

    response = token_session.post(
        domain_url + "/api/search/%s" % query,
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
        domain_url + "/api/search/%s" % str(uuid4())
    )

    with pytest.raises(JSONDecodeError):
        response.json()

    assert response.status_code == 204


def test_search_unauthorized(domain_url):
    response = requests.post(
        domain_url + "/api/search/query",
    )

    data = response.json()
    ErrorSchema().load(data)
    assert response.status_code == 401
