import pytest
from elasticsearch_dsl import Index
from uuid import uuid4

from backend.service import SessionService
from backend.model import Session
from backend.tests.factories import SessionFactory, ProductFactory
from backend.errors.no_content_error import NoContentError
from backend.errors.not_found_error import NotFoundError


@pytest.fixture(scope="session")
def service():
    service = SessionService()
    return service


def test_count_products(service, es_object):
    session_id = str(uuid4())
    prod_list = ProductFactory.create_batch(2, sessionid=session_id)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    result = service._SessionService__count_products(session_id)
    assert result == 2


def test_session_service_select(service, es_object):
    session_obj = SessionFactory.create()
    session_obj.save(using=es_object.connection)

    prod_list = ProductFactory.create_batch(2, sessionid=session_obj.meta["id"])
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    results = service.select()
    assert len(results) > 0

    session_gender = "I_test_session_service_select"
    session_name = str(uuid4())
    session_obj = SessionFactory.create(gender=session_gender, name=session_name)
    session_obj.save(using=es_object.connection)

    prod_list = ProductFactory.create_batch(2, sessionid=session_obj.meta["id"])
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    results = service.select(gender=session_gender)
    assert len(results) == 1
    assert results[0]["total"] == 2

    results = service.select(name=session_name)
    assert len(results) == 1
    assert results[0]["total"] == 2

    with pytest.raises(NoContentError):
        service.select(gender=str(uuid4()))

    with pytest.raises(NoContentError):
        service.select(name=str(uuid4()))


def test_session_service_select_by_id(service, es_object):
    session_obj = SessionFactory.create()
    session_obj.save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_by_id(session_obj.meta["id"])
    assert results is not None
    assert type(results) is Session

    with pytest.raises(NotFoundError):
        service.select_by_id(str(uuid4()))
