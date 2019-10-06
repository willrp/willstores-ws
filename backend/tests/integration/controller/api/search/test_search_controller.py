import pytest
from flask import json
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory
from backend.util.response.search_results import SearchResultsSchema
from backend.util.response.error import ErrorSchema


def test_search_controller(token_app, es_object):
    query = str(uuid4())
    prod_list = [
        ProductFactory.create(name=query),
        ProductFactory.create(gender=query),
        ProductFactory.create(kind=query),
        ProductFactory.create(brand=query)
    ]
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    with token_app.test_client() as client:
        response = client.post(
            "api/search/%s" % query
        )

    data = json.loads(response.data)
    SearchResultsSchema().load(data)
    assert response.status_code == 200
    assert data["total"] == 4

    with token_app.test_client() as client:
        response = client.post(
            "api/search/%s" % query,
            json={
                "pricerange": {
                    "min": 1,
                    "max": 500
                }
            }
        )

    data = json.loads(response.data)
    SearchResultsSchema().load(data)
    assert response.status_code == 200
    assert data["total"] == 4

    with token_app.test_client() as client:
        response = client.post(
            "api/search/%s" % query,
            json={
                "pricerange": {
                    "min": 10000,
                    "max": 20000
                }
            }
        )

    with pytest.raises(JSONDecodeError):
        json.loads(response.data)

    assert response.status_code == 204

    with token_app.test_client() as client:
        response = client.post(
            "api/search/%s" % str(uuid4())
        )

    with pytest.raises(JSONDecodeError):
        json.loads(response.data)

    assert response.status_code == 204


def test_search_controller_unauthorized(flask_app):
    with flask_app.test_client() as client:
        response = client.post(
            "api/search/query",
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 401
