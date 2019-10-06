import pytest
from elasticsearch.exceptions import ConnectionError

from backend.dao.es import ES


def test_es():
    ES().connection


def test_es_endpoint_connection_error(monkeypatch):
    with monkeypatch.context() as m:
        m.setenv("ES_URL", "https://notaserver.com")

        with pytest.raises(ConnectionError):
            ES().connection
