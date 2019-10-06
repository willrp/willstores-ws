from flask import json
from elasticsearch_dsl import Index
from uuid import uuid4

from backend.tests.factories import ProductFactory
from backend.util.response.product_results import ProductResultsSchema
from backend.util.response.error import ErrorSchema


def test_product_controller(token_app, es_object):
    prod_obj = ProductFactory.create()
    prod_obj.save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    prod_id = prod_obj.meta["id"]

    with token_app.test_client() as client:
        response = client.get(
            "api/product/%s" % prod_id
        )

    data = json.loads(response.data)
    ProductResultsSchema().load(data)
    assert response.status_code == 200

    with token_app.test_client() as client:
        response = client.get(
            "api/product/%s" % str(uuid4())
        )

    data = json.loads(response.data)
    assert data == {}
    assert response.status_code == 404


def test_product_controller_unauthorized(flask_app):
    with flask_app.test_client() as client:
        response = client.get(
            "api/product/1",
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 401
