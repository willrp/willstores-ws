import pytest
from elasticsearch_dsl import Index, Search
from uuid import uuid4

from backend.service import ProductService
from backend.model import Product
from backend.tests.factories import ProductFactory
from backend.errors.no_content_error import NoContentError
from backend.errors.not_found_error import NotFoundError
from backend.errors.request_error import ValidationError


@pytest.fixture(scope="session")
def service():
    service = ProductService()
    return service


def test_product_service_products_count(service, es_object):
    prod_list = ProductFactory.create_batch(2)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    result = service.products_count()
    assert result > 0


def test_product_service_super_discounts(service, es_object):
    prod_list = ProductFactory.create_batch(2)
    [prod_obj.save(using=es_object.connection) for prod_obj in prod_list]
    Index("store", using=es_object.connection).refresh()

    results = service.super_discounts()
    assert len(results) > 0
    assert type(results[0]) == Product

    test_alt_id = "I_test_product_service_super_discounts"

    ProductFactory.create(gender=test_alt_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.super_discounts(gender=test_alt_id)
    assert len(results) == 1
    assert type(results[0]) == Product

    with pytest.raises(NoContentError):
        results = service.super_discounts(gender=str(uuid4()))


def test_product_service_search(service, es_object):
    search = service._ProductService__search()
    assert type(search) == Search

    service._ProductService__search(query="query", gender="gender", sessionid="sessionid", sessionname="sessionname", brand="brand", kind="kind", pricerange={"min": 1.0, "max": 100.0})
    assert type(search) == Search


def test_product_service_select_pricerange(service, es_object):
    ProductFactory.create(price={"outlet": 10.0, "retail": 100.0}).save(using=es_object.connection)
    ProductFactory.create(price={"outlet": 20.0, "retail": 120.0}).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_pricerange()
    for key in ["min", "max"]:
        assert key in results
        assert len(results.keys()) == 2
        assert results["min"] <= results["max"]

    test_alt_id = "I_test_product_service_select_pricerange"
    test_id = str(uuid4())

    ProductFactory.create(gender=test_alt_id, price={"outlet": 10.0, "retail": 100.0}).save(using=es_object.connection)
    ProductFactory.create(gender=test_alt_id, price={"outlet": 20.0, "retail": 120.0}).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_pricerange(gender=test_alt_id)
    assert results["min"] == 10.0
    assert results["max"] == 20.0

    with pytest.raises(NoContentError):
        service.select_pricerange(gender=str(uuid4()))

    ProductFactory.create(sessionid=test_id, price={"outlet": 10.0, "retail": 100.0}).save(using=es_object.connection)
    ProductFactory.create(sessionid=test_id, price={"outlet": 20.0, "retail": 120.0}).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_pricerange(sessionid=test_id)
    assert results["min"] == 10.0
    assert results["max"] == 20.0

    with pytest.raises(NoContentError):
        service.select_pricerange(sessionid=str(uuid4()))

    ProductFactory.create(sessionname=test_id, price={"outlet": 10.0, "retail": 100.0}).save(using=es_object.connection)
    ProductFactory.create(sessionname=test_id, price={"outlet": 20.0, "retail": 120.0}).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_pricerange(sessionname=test_id)
    assert results["min"] == 10.0
    assert results["max"] == 20.0

    with pytest.raises(NoContentError):
        service.select_pricerange(sessionname=str(uuid4()))

    ProductFactory.create(brand=test_id, price={"outlet": 10.0, "retail": 100.0}).save(using=es_object.connection)
    ProductFactory.create(brand=test_id, price={"outlet": 20.0, "retail": 120.0}).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_pricerange(brand=test_id)
    assert results["min"] == 10.0
    assert results["max"] == 20.0

    with pytest.raises(NoContentError):
        service.select_pricerange(brand=str(uuid4()))

    ProductFactory.create(kind=test_id, price={"outlet": 10.0, "retail": 100.0}).save(using=es_object.connection)
    ProductFactory.create(kind=test_id, price={"outlet": 20.0, "retail": 120.0}).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_pricerange(kind=test_id)
    assert results["min"] == 10.0
    assert results["max"] == 20.0

    with pytest.raises(NoContentError):
        service.select_pricerange(kind=str(uuid4()))

    results = service.select_pricerange(query=test_id)
    assert results["min"] == 10.0
    assert results["max"] == 20.0

    results = service.select_pricerange(query=test_alt_id)
    assert results["min"] == 10.0
    assert results["max"] == 20.0

    with pytest.raises(NoContentError):
        service.select_pricerange(query=str(uuid4()))


def test_product_service_get_total(service, es_object):
    ProductFactory.create().save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.get_total()
    assert results > 0

    test_alt_id = "I_test_product_service_get_total"
    test_id = str(uuid4())

    ProductFactory.create(gender=test_alt_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.get_total(gender=test_alt_id)
    assert results == 1

    results = service.get_total(gender=str(uuid4()))
    assert results == 0

    ProductFactory.create(sessionid=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.get_total(sessionid=test_id)
    assert results == 1

    results = service.get_total(sessionid=str(uuid4()))
    assert results == 0

    ProductFactory.create(sessionname=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.get_total(sessionname=test_id)
    assert results == 1

    results = service.get_total(sessionname=str(uuid4()))
    assert results == 0

    ProductFactory.create(brand=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.get_total(brand=test_id)
    assert results == 1

    results = service.get_total(brand=str(uuid4()))
    assert results == 0

    ProductFactory.create(kind=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.get_total(kind=test_id)
    assert results == 1

    results = service.get_total(kind=str(uuid4()))
    assert results == 0

    results = service.get_total(pricerange={"min": 1.0, "max": 100.0})
    assert results > 0

    results = service.get_total(pricerange={"min": 10000.0, "max": 20000.0})
    assert results == 0

    results = service.get_total(query=test_id)
    assert results == 2

    results = service.get_total(query=test_alt_id)
    assert results == 1

    results = service.get_total(query=str(uuid4()))
    assert results == 0


def test_product_service_select_brands(service, es_object):
    ProductFactory.create().save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_brands()
    assert len(results) > 0

    test_alt_id = "I_test_product_service_select_brands"
    test_id = str(uuid4())

    ProductFactory.create(gender=test_alt_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_brands(gender=test_alt_id)
    assert len(results) == 1
    for key in ["brand", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_brands(gender=str(uuid4()))

    ProductFactory.create(sessionid=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_brands(sessionid=test_id)
    assert len(results) == 1
    for key in ["brand", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_brands(sessionid=str(uuid4()))

    ProductFactory.create(sessionname=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_brands(sessionname=test_id)
    assert len(results) == 1
    for key in ["brand", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_brands(sessionname=str(uuid4()))

    ProductFactory.create(brand=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_brands(brand=test_id)
    assert len(results) == 1
    for key in ["brand", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_brands(brand=str(uuid4()))

    ProductFactory.create(kind=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_brands(kind=test_id)
    assert len(results) == 1
    for key in ["brand", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_brands(kind=str(uuid4()))

    results = service.select_brands(pricerange={"min": 1.0, "max": 100.0})
    assert len(results) > 0

    with pytest.raises(NoContentError):
        service.select_brands(pricerange={"min": 10000.0, "max": 20000.0})

    results = service.select_brands(query=test_id)
    assert len(results) == 2
    for key in ["brand", "amount"]:
        assert key in results[0]

    results = service.select_brands(query=test_alt_id)
    assert len(results) == 1
    for key in ["brand", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_brands(query=str(uuid4()))


def test_product_service_select_kinds(service, es_object):
    ProductFactory.create().save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_kinds()
    assert len(results) > 0

    test_alt_id = "I_test_product_service_select_kinds"
    test_id = str(uuid4())

    ProductFactory.create(gender=test_alt_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_kinds(gender=test_alt_id)
    assert len(results) == 1
    for key in ["kind", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_kinds(gender=str(uuid4()))

    ProductFactory.create(sessionid=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_kinds(sessionid=test_id)
    assert len(results) == 1
    for key in ["kind", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_kinds(sessionid=str(uuid4()))

    ProductFactory.create(sessionname=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_kinds(sessionname=test_id)
    assert len(results) == 1
    for key in ["kind", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_kinds(sessionname=str(uuid4()))

    ProductFactory.create(brand=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_kinds(brand=test_id)
    assert len(results) == 1
    for key in ["kind", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_kinds(brand=str(uuid4()))

    ProductFactory.create(kind=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select_kinds(kind=test_id)
    assert len(results) == 1
    for key in ["kind", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_kinds(kind=str(uuid4()))

    results = service.select_kinds(pricerange={"min": 1.0, "max": 100.0})
    assert len(results) > 0

    with pytest.raises(NoContentError):
        service.select_kinds(pricerange={"min": 10000.0, "max": 20000.0})

    results = service.select_kinds(query=test_id)
    assert len(results) == 2
    for key in ["kind", "amount"]:
        assert key in results[0]

    results = service.select_kinds(query=test_alt_id)
    assert len(results) == 1
    for key in ["kind", "amount"]:
        assert key in results[0]

    with pytest.raises(NoContentError):
        service.select_kinds(query=str(uuid4()))


def test_product_service_select(service, es_object):
    ProductFactory.create().save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select()
    assert len(results) > 0

    test_alt_id = "I_test_product_service_select"
    test_id = str(uuid4())

    ProductFactory.create(gender=test_alt_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select(gender=test_alt_id)
    assert len(results) == 1
    assert type(results[0]) == Product

    with pytest.raises(NoContentError):
        service.select(gender=str(uuid4()))

    ProductFactory.create(sessionid=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select(sessionid=test_id)
    assert len(results) == 1
    assert type(results[0]) == Product

    with pytest.raises(NoContentError):
        service.select(sessionid=str(uuid4()))

    ProductFactory.create(sessionname=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select(sessionname=test_id)
    assert len(results) == 1
    assert type(results[0]) == Product

    with pytest.raises(NoContentError):
        service.select(sessionname=str(uuid4()))

    ProductFactory.create(brand=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select(brand=test_id)
    assert len(results) == 1
    assert type(results[0]) == Product

    with pytest.raises(NoContentError):
        service.select(brand=str(uuid4()))

    ProductFactory.create(kind=test_id).save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    results = service.select(kind=test_id)
    assert len(results) == 1
    assert type(results[0]) == Product

    with pytest.raises(NoContentError):
        service.select(kind=str(uuid4()))

    results = service.select(pricerange={"min": 1.0, "max": 100.0})
    assert len(results) > 0
    assert type(results[0]) == Product

    with pytest.raises(NoContentError):
        service.select(pricerange={"min": 10000.0, "max": 20000.0})

    results = service.select(query=test_id)
    assert len(results) == 2
    assert type(results[0]) == Product

    results = service.select(query=test_alt_id)
    assert len(results) == 1
    assert type(results[0]) == Product

    with pytest.raises(NoContentError):
        service.select(query=str(uuid4()))


def test_product_service_select_by_id(service, es_object):
    obj = ProductFactory.create()
    obj.save(using=es_object.connection)
    Index("store", using=es_object.connection).refresh()

    obj_id = obj.meta["id"]

    results = service.select_by_id(obj_id)
    assert type(results) == Product
    assert results.meta["id"] == obj_id

    fake_id = str(uuid4())

    with pytest.raises(NotFoundError):
        service.select_by_id(fake_id)


def test_product_service_select_by_item_list(service, es_object):
    price = {"outlet": 10.0, "retail": 20.0}
    item_list = []
    for i in range(3):
        obj = ProductFactory.create(price=price)
        obj.save(using=es_object.connection)
        item_list.append({"item_id": obj.meta["id"], "amount": i+1})

    Index("store", using=es_object.connection).refresh()

    results, total = service.select_by_item_list(item_list)
    assert len(results) == len(item_list)
    item_id_list = [item["item_id"] for item in item_list]
    for obj in results:
        assert type(obj) == Product
        assert obj.meta["id"] in item_id_list

    assert total["outlet"] == 60.0
    assert total["retail"] == 120.0

    with pytest.raises(NoContentError):
        service.select_by_item_list([])

    fake_item_list = [{"item_id": str(uuid4()), "amount": 2} for x in range(2)]

    with pytest.raises(NoContentError):
        service.select_by_item_list(fake_item_list)

    over_item_list = item_list + fake_item_list

    with pytest.raises(ValidationError):
        service.select_by_item_list(over_item_list)
