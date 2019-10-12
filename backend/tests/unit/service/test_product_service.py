import pytest
from unittest.mock import MagicMock
from elasticsearch_dsl import Search

from backend.service import ProductService
from backend.errors.no_content_error import NoContentError
from backend.errors.not_found_error import NotFoundError
from backend.errors.request_error import ValidationError


@pytest.fixture(scope="function", autouse=True)
def service_mocker(mocker, service_init_mock):
    mocker.patch("backend.service.ProductService.__init__", new=service_init_mock)


@pytest.fixture(scope="function")
def service():
    service = ProductService()
    return service


def test_product_service_products_count(mocker, service):
    mock_execute = MagicMock()
    mock_execute.hits.total = 15
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        result = service.products_count()
        assert result == 15


def test_product_service_super_discounts(mocker, service):
    with mocker.patch.object(Search, "execute", return_value=[MagicMock(autospec=True) for i in range(3)]):
        results = service.super_discounts()
        assert len(results) == 3

        results = service.super_discounts(gender="gender")
        assert len(results) == 3

    with mocker.patch.object(Search, "execute", return_value=[]):
        with pytest.raises(NoContentError):
            service.super_discounts()


def test_product_service_search(mocker, service):
    with mocker.patch.object(Search, "execute", return_value=[MagicMock(autospec=True) for i in range(3)]):
        service._ProductService__search()
        service._ProductService__search(query="query", gender="gender", sessionid="sessionid", sessionname="sessionname", brand="brand", kind="kind", pricerange={"min": 1.0, "max": 100.0})


def test_product_service_select_pricerange(mocker, service):
    mock_execute = MagicMock()
    mock_execute.aggs.minprice.value = 100
    mock_execute.aggs.maxprice.value = 200
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        results = service.select_pricerange()
        assert results["min"] == 100
        assert results["max"] == 200

        results = service.select_pricerange(query="query", gender="gender", sessionid="sessionid", sessionname="sessionname", brand="brand", kind="kind")
        assert results["min"] == 100
        assert results["max"] == 200

    with mocker.patch.object(Search, "execute", return_value=[]):
        with pytest.raises(NoContentError):
            service.select_pricerange()


def test_product_service_get_total(mocker, service):
    mock_execute = MagicMock()
    mock_execute.hits.total = 10
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        results = service.get_total()
        assert results == 10

        results = service.get_total(query="query", gender="gender", sessionid="sessionid", sessionname="sessionname", brand="brand", kind="kind", pricerange={"min": 1.0, "max": 100.0})
        assert results == 10


def test_product_service_select_brands(mocker, service):
    mock_execute = MagicMock()
    mock_execute.aggs.brands.buckets = [MagicMock(key="A", doc_count=10), MagicMock(key="B", doc_count=5)]
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        results = service.select_brands()
        assert len(results) == 2
        for key in ["brand", "amount"]:
            assert key in results[0]

        results = service.select_brands(query="query", gender="gender", sessionid="sessionid", sessionname="sessionname", brand="brand", kind="kind", pricerange={"min": 1.0, "max": 100.0})
        assert len(results) == 2
        for key in ["brand", "amount"]:
            assert key in results[0]

    mock_execute = MagicMock()
    mock_execute.aggs.brands.buckets = []
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        with pytest.raises(NoContentError):
            service.select_brands()


def test_product_service_select_kinds(mocker, service):
    mock_execute = MagicMock()
    mock_execute.aggs.kinds.buckets = [MagicMock(key="A", doc_count=10), MagicMock(key="B", doc_count=5)]
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        results = service.select_kinds()
        assert len(results) == 2
        for key in ["kind", "amount"]:
            assert key in results[0]

        results = service.select_kinds(query="query", gender="gender", sessionid="sessionid", sessionname="sessionname", brand="brand", kind="kind", pricerange={"min": 1.0, "max": 100.0})
        assert len(results) == 2
        for key in ["kind", "amount"]:
            assert key in results[0]

    mock_execute = MagicMock()
    mock_execute.aggs.kinds.buckets = []
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        with pytest.raises(NoContentError):
            service.select_kinds()


def test_product_service_select(mocker, service):
    with mocker.patch.object(Search, "execute", return_value=[MagicMock(autospec=True) for i in range(3)]):
        results = service.select()
        assert len(results) == 3

        results = service.select(query="query", gender="gender", sessionid="sessionid", sessionname="sessionname", brand="brand", kind="kind", pricerange={"min": 1.0, "max": 100.0})
        assert len(results) == 3

    with mocker.patch.object(Search, "execute", return_value=[]):
        with pytest.raises(NoContentError):
            service.select()


def test_product_service_select_by_id(mocker, service):
    with mocker.patch.object(Search, "execute", return_value=[MagicMock(autospec=True)]):
        service.select_by_id("id")

    with mocker.patch.object(Search, "execute", return_value=[]):
        with pytest.raises(NotFoundError):
            service.select_by_id("id")


def test_product_service_select_by_id_list(mocker, service):
    mock_execute = MagicMock()
    mock_execute.meta = {"id": "id"}
    mock_execute.price = MagicMock(outlet=10.0, retail=20.0)
    mock_execute.price.get_dict.return_value = {"outlet": 10.0, "retail": 20.0, "symbol": "£"}
    with mocker.patch.object(Search, "execute", return_value=[mock_execute for i in range(2)]):
        results, total = service.select_by_id_list(["id", "id"])
        assert len(results) == 2
        assert total["outlet"] == 20.0
        assert total["retail"] == 40.0

        results = service.select_by_id_list([])
        assert len(results) == 2

    with mocker.patch.object(Search, "execute", return_value=[]):
        with pytest.raises(NoContentError):
            service.select_by_id_list([])

    with mocker.patch.object(Search, "execute", return_value=[mock_execute for i in range(2)]):
        with pytest.raises(ValidationError):
            service.select_by_id_list(["notid", "notid"])
