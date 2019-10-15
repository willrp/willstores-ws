import pytest
from flask import json
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory
from backend.util.response.products_list import ProductsListSchema
from backend.util.response.error import ErrorSchema


def test_product_list_controller(token_app, es_object):
    price = {"outlet": 10.0, "retail": 20.0}
    prod_list = ProductFactory.create_batch(2, price=price)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    prod_item_list = [{"item_id": p.meta["id"], "amount": 3} for p in prod_list]

    with token_app.test_client() as client:
        response = client.post(
            "api/product/list",
            json={
                "item_list": prod_item_list,
            }
        )

    data = json.loads(response.data)
    ProductsListSchema().load(data)
    assert response.status_code == 200
    assert len(data["products"]) == 2
    assert data["total"]["outlet"] == 60.0
    assert data["total"]["retail"] == 120.0

    fake_item_list = [{"item_id": str(uuid4()), "amount": 1} for p in range(2)]

    with token_app.test_client() as client:
        response = client.post(
            "api/product/list",
            json={
                "item_list": fake_item_list
            }
        )

    with pytest.raises(JSONDecodeError):
        json.loads(response.data)

    assert response.status_code == 204

    with token_app.test_client() as client:
        response = client.post(
            "api/product/list",
            json={
                "id_list": prod_item_list + fake_item_list,
            }
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 400


def test_product_list_controller_unauthorized(flask_app):
    with flask_app.test_client() as client:
        response = client.post(
            "api/product/list",
        )

    data = json.loads(response.data)
    ErrorSchema().load(data)
    assert response.status_code == 401
