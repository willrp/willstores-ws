import requests
from elasticsearch_dsl import Index

from backend.tests.factories import ProductFactory
from backend.util.response.products_count import ProductsCountSchema
from backend.util.response.error import ErrorSchema


def test_start(domain_url, es_object, token_session):
    prod_list = ProductFactory.create_batch(2)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    response = token_session.get(
        domain_url + "/api/start"
    )

    data = response.json()
    ProductsCountSchema().load(data)
    assert response.status_code == 200
    assert data["count"] > 0


def test_start_unauthorized(domain_url):
    response = requests.get(
        domain_url + "/api/start",
    )

    data = response.json()
    ErrorSchema().load(data)
    assert response.status_code == 401
