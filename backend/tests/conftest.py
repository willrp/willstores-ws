import pytest
import re
import os
from dotenv import load_dotenv, find_dotenv
from elasticsearch_dsl import Index

from backend import create_app
from backend.dao.es import ES


@pytest.fixture(scope="session")
def domain_ip():
    load_dotenv(find_dotenv())
    return os.getenv("TEST_DOMAIN_IP")


@pytest.fixture(scope="session")
def es_url(domain_ip):
    test_es = os.getenv("ES_URL")
    TEST_ES_URL = re.sub("TEST_DOMAIN_IP", domain_ip, test_es)
    return TEST_ES_URL


@pytest.fixture(scope="session")
def flask_app():
    app = create_app(flask_env="test")
    return app


@pytest.fixture(scope="session")
def es_object():
    es = ES()
    yield es


@pytest.fixture(scope="session", autouse=True)
def setup_teardown(es_url, es_object):
    os.environ["ES_URL"] = es_url
    yield
    Index("store", using=es_object.connection).delete()


@pytest.fixture(scope="session")
def jwt_test_token():
    return os.getenv("ACCESS_TOKEN")
