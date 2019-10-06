import requests
from elasticsearch_dsl import Index
from uuid import uuid4

from backend.tests.factories import ProductFactory
from backend.util.response.product_results import ProductResultsSchema
from backend.util.response.error import ErrorSchema


def test_product(domain_url, es_object, token_session):
    prod_obj = ProductFactory.create()
    prod_obj.save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    prod_id = prod_obj.meta["id"]

    response = token_session.get(
        domain_url + "/api/product/%s" % prod_id
    )

    data = response.json()
    ProductResultsSchema().load(data)
    assert response.status_code == 200

    response = token_session.get(
        domain_url + "/api/product/%s" % str(uuid4())
    )

    data = response.json()
    assert data == {}
    assert response.status_code == 404


def test_product_unauthorized(domain_url):
    response = requests.get(
        domain_url + "/api/product/1",
    )

    data = response.json()
    ErrorSchema().load(data)
    assert response.status_code == 401
