import pytest
from unittest.mock import MagicMock
from elasticsearch_dsl.search import Search

from backend.service import SessionService
from backend.model import Session, Product
from backend.tests.factories import SessionFactory, ProductFactory
from backend.errors.no_content_error import NoContentError
from backend.errors.not_found_error import NotFoundError


@pytest.fixture(scope="function", autouse=True)
def service_mocker(mocker, service_init_mock):
    mocker.patch("backend.service.SessionService.__init__", new=service_init_mock)


@pytest.fixture(scope="function")
def service():
    service = SessionService()
    return service


def test_count_products(mocker, service):
    mock_execute = MagicMock()
    mock_execute.hits.total = 10
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        result = service._SessionService__count_products("session_id")
        assert result == 10


def test_sessions_select(mocker, service):
    mock_execute = MagicMock(autospec=True)
    mock_execute.get_dict.return_value = {"name": "Session"}
    with mocker.patch.object(Search, "execute", return_value=[mock_execute for i in range(3)]):
        with mocker.patch.object(SessionService, "_SessionService__count_products", return_value=2):
            results = service.select()
            assert len(results) == 3
            assert results[0]["total"] == 2

            results = service.select(gender="gender")
            assert len(results) == 3
            assert results[0]["total"] == 2

            results = service.select(name="name")
            assert len(results) == 3
            assert results[0]["total"] == 2

    with mocker.patch.object(Search, "execute", return_value=[]):
        with pytest.raises(NoContentError):
            service.select()


def test_sessions_select_by_id(mocker, service, es_object):
    mock_execute = MagicMock()
    mock_execute.hits = [MagicMock(autospec=True)]
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        results = service.select_by_id("session_id")
        assert results is not None

    mock_execute = MagicMock()
    mock_execute.hits = []
    with mocker.patch.object(Search, "execute", return_value=mock_execute):
        with pytest.raises(NotFoundError):
            service.select_by_id("session_id")\
