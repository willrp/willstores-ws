import pytest
import requests
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory
from backend.util.response.products_total import ProductTotalSchema
from backend.util.response.error import ErrorSchema


def test_product_list(domain_url, es_object, token_session):
    price = {"outlet": 10.0, "retail": 20.0}
    prod_list = ProductFactory.create_batch(2, price=price)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    prod_id_list = [p.meta["id"] for p in prod_list]

    response = token_session.post(
        domain_url + "/api/product/total",
        json={
            "id_list": prod_id_list,
        }
    )

    data = response.json()
    ProductTotalSchema().load(data)
    assert response.status_code == 200
    assert data["total"]["outlet"] == 20.0
    assert data["total"]["retail"] == 40.0

    response = token_session.post(
        domain_url + "/api/product/total",
        json={
            "id_list": [str(uuid4()) for i in range(2)]
        }
    )

    with pytest.raises(JSONDecodeError):
        response.json()

    assert response.status_code == 204

    response = token_session.post(
        domain_url + "/api/product/total",
        json={
            "id_list": prod_id_list.append(str(uuid4())),
        }
    )

    data = response.json()
    ErrorSchema().load(data)
    assert response.status_code == 400


def test_product_list_unauthorized(domain_url):
    response = requests.post(
        domain_url + "/api/product/total",
    )

    data = response.json()
    ErrorSchema().load(data)
    assert response.status_code == 401
