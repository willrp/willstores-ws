import pytest
import requests
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory, SessionFactory
from backend.util.response.gender_results import GenderResultsSchema
from backend.util.response.error import ErrorSchema


def test_gender_controller(domain_url, es_object, token_session):
    session_obj = SessionFactory.create(gender="Women")
    session_obj.save(using=es_object.connection)
    prod_list = ProductFactory.create_batch(2, gender="Women", sessionid=session_obj.meta["id"])
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    response = token_session.post(
        domain_url + "/api/gender/women"
    )

    data = response.json()
    GenderResultsSchema().load(data)
    assert response.status_code == 200
    assert len(data["discounts"]) >= 2

    response = token_session.post(
        domain_url + "/api/gender/women",
        json={
            "amount": 1
        }
    )

    data = response.json()
    GenderResultsSchema().load(data)
    assert response.status_code == 200
    assert len(data["discounts"]) == 1

    response = token_session.post(
        domain_url + "/api/gender/%s" % str(uuid4())
    )

    with pytest.raises(JSONDecodeError):
        response.json()

    assert response.status_code == 204


def test_gender_controller_unauthorized(domain_url):
    response = requests.post(
        domain_url + "/api/gender/women",
    )

    data = response.json()
    ErrorSchema().load(data)
    assert response.status_code == 401
