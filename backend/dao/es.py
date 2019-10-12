import os
from elasticsearch import Elasticsearch

from ..model import Product, Session


class ES(object):
    def __init__(self) -> None:
        self.__conn = None

    @property
    def connection(self):
        if(self.__conn is None):
            self.__conn = Elasticsearch(os.getenv("ES_URL"))
            Session.init(using=self.__conn)
            Product.init(using=self.__conn)
        return self.__conn
