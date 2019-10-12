import pytest
from flask import json
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory
from backend.util.response.products_total import ProductTotalSchema
from backend.util.response.error import ErrorSchema


def test_product_total_controller(token_app, es_object):
    price = {"outlet": 10.0, "retail": 20.0}
    prod_list = ProductFactory.create_batch(2, price=price)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    prod_id_list = [p.meta["id"] for p in prod_list]

    with token_app.test_client() as client:
        response = client.post(
            "api/product/total",
            json={
                "id_list": prod_id_list,
            }
        )

    data = json.loads(response.data)
    ProductTotalSchema().load(data)
    assert response.status_code == 200
    assert data["total"]["outlet"] == 20.0
    assert data["total"]["retail"] == 40.0

    with token_app.test_client() as client:
        response = client.post(
            "api/product/total",
            json={
                "id_list": [str(uuid4()) for i in range(2)]
            }
        )

    with pytest.raises(JSONDecodeError):
        json.loads(response.data)

    assert response.status_code == 204

    with token_app.test_client() as client:
        response = client.post(
            "api/product/total",
            json={
                "id_list": prod_id_list.append(str(uuid4())),
            }
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400


def test_product_total_controller_unauthorized(flask_app):
    with flask_app.test_client() as client:
        response = client.post(
            "api/product/total",
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 401
