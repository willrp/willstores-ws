import pytest
import requests
from elasticsearch_dsl import Index
from uuid import uuid4
from json.decoder import JSONDecodeError

from backend.tests.factories import ProductFactory, SessionFactory
from backend.util.response.session_results import SessionResultsSchema
from backend.util.response.error import ErrorSchema


def test_session(domain_url, es_object, token_session):
    session_obj = SessionFactory.create(gender="Women")
    session_obj.save(using=es_object.connection)
    session_id = session_obj.meta["id"]
    prod_list = ProductFactory.create_batch(2, gender="Women", sessionid=session_id)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    response = token_session.post(
        domain_url + "/api/session/%s" % session_id
    )

    data = response.json()
    SessionResultsSchema().load(data)
    assert response.status_code == 200
    assert data["sessions"][0]["gender"] == session_obj.gender
    assert data["total"] == 2

    response = token_session.post(
        domain_url + "/api/session/%s" % session_id,
        json={
            "pricerange": {
                "min": 1,
                "max": 500
            }
        }
    )

    data = response.json()
    SessionResultsSchema().load(data)
    assert response.status_code == 200
    assert data["sessions"][0]["gender"] == session_obj.gender
    assert data["total"] == 2

    response = token_session.post(
        domain_url + "/api/session/%s" % session_id,
        json={
            "pricerange": {
                "min": 10000,
                "max": 20000
            }
        }
    )

    with pytest.raises(JSONDecodeError):
        response.json()

    assert response.status_code == 204

    response = token_session.post(
        domain_url + "/api/session/%s" % str(uuid4())
    )

    data = response.json()
    assert data == {}
    assert response.status_code == 404


def test_session_unauthorized(domain_url):
    response = requests.post(
        domain_url + "/api/session/1",
    )

    data = response.json()
    ErrorSchema().load(data)
    assert response.status_code == 401
