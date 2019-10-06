import pytest
from flask import json
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory, SessionFactory
from backend.util.response.gender_results import GenderResultsSchema
from backend.util.response.error import ErrorSchema


def test_gender_controller(token_app, es_object):
    session_obj = SessionFactory.create(gender="Women")
    session_obj.save(using=es_object.connection)
    prod_list = ProductFactory.create_batch(2, gender="Women", sessionid=session_obj.meta["id"])
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    with token_app.test_client() as client:
        response = client.post(
            "api/gender/women"
        )

    data = json.loads(response.data)
    GenderResultsSchema().load(data)
    assert response.status_code == 200
    assert len(data["discounts"]) >= 2

    with token_app.test_client() as client:
        response = client.post(
            "api/gender/women",
            json={
                "amount": 1
            }
        )

    data = json.loads(response.data)
    GenderResultsSchema().load(data)
    assert response.status_code == 200
    assert len(data["discounts"]) == 1

    with token_app.test_client() as client:
        response = client.post(
            "api/gender/%s" % str(uuid4())
        )

    with pytest.raises(JSONDecodeError):
        json.loads(response.data)

    assert response.status_code == 204


def test_gender_controller_unauthorized(flask_app):
    with flask_app.test_client() as client:
        response = client.post(
            "api/gender/women",
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 401
