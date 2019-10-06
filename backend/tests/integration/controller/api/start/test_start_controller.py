from flask import json
from elasticsearch_dsl import Index

from backend.tests.factories import ProductFactory
from backend.util.response.total_products import TotalProductsSchema
from backend.util.response.error import ErrorSchema


def test_start_controller(token_app, es_object):
    prod_list = ProductFactory.create_batch(2)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    with token_app.test_client() as client:
        response = client.get(
            "api/start"
        )

    data = json.loads(response.data)
    TotalProductsSchema().load(data)
    assert response.status_code == 200
    assert data["count"] > 0


def test_start_controller_unauthorized(flask_app):
    with flask_app.test_client() as client:
        response = client.get(
            "api/start",
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 401
