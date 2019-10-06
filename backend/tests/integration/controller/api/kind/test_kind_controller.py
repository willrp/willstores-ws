import pytest
from flask import json
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory
from backend.util.response.search_results import SearchResultsSchema
from backend.util.response.error import ErrorSchema


def test_kind_controller(token_app, es_object):
    kind = str(uuid4())
    prod_list = ProductFactory.create_batch(2, kind=kind)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    with token_app.test_client() as client:
        response = client.post(
            "api/kind/%s" % kind
        )

    data = json.loads(response.data)
    SearchResultsSchema().load(data)
    assert response.status_code == 200
    assert data["total"] == 2

    with token_app.test_client() as client:
        response = client.post(
            "api/kind/%s" % kind,
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
    assert data["total"] == 2

    with token_app.test_client() as client:
        response = client.post(
            "api/kind/%s" % kind,
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
            "api/kind/%s" % str(uuid4())
        )

    with pytest.raises(JSONDecodeError):
        json.loads(response.data)

    assert response.status_code == 204


def test_kind_controller_unauthorized(flask_app):
    with flask_app.test_client() as client:
        response = client.post(
            "api/kind/1",
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 401
