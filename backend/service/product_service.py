from typing import List
from elasticsearch_dsl import Search, Q

from backend.model import Product
from backend.dao.es import ES
from backend.errors.no_content_error import NoContentError
from backend.errors.not_found_error import NotFoundError


class ProductService(object):
    def __init__(self):
        self.es = ES().connection

    def total_products(self) -> int:
        s = Product.search(using=self.es)
        s = s.filter("match_all")[:0]
        s = s.query({"range": {"price.retail": {"gt": 0.0}}}).query({"range": {"price.outlet": {"gt": 0.0}}})
        results = s.execute()
        return results.hits.total

    def super_discounts(self, gender=None, amount=10) -> List[Product]:
        s = Product.search(using=self.es)
        s = s[:amount]
        if gender is not None:
            s = s.filter("term", gender=gender.lower())
        s = s.query({"range": {"price.retail": {"gt": 0.0}}}).query({"range": {"price.outlet": {"gt": 0.0}}})
        s = s.sort({"_script": {"type": "number",
                                "script": "(1.0 - (doc['price.outlet'].value / "
                                          "doc['price.retail'].value)) * 100",
                                "order": "desc"}})
        results = s.execute()

        if not results:
            raise NoContentError()
        else:
            return results

    def __search(self, query=None, gender=None, sessionid=None, sessionname=None, brand=None,
                kind=None, pricerange=None) -> Search:
        s = Product.search(using=self.es)
        if query is not None:
            q = Q("multi_match", query=query, type="most_fields", fields=["kind", "brand", "gender", "name"])
            s = s.query(q)
        if gender is not None:
            s = s.filter("term", gender=gender.lower())
        if sessionid is not None:
            s = s.filter({"term": {"sessionid.keyword": sessionid}})
        if sessionname is not None:
            s = s.query("match_phrase", sessionname="\"%s\"" % sessionname)
        if brand is not None:
            s = s.query("match_phrase", brand="\"%s\"" % brand)
        if kind is not None:
            s = s.query("match_phrase", kind="\"%s\"" % kind)
        if pricerange is not None:
            s = s.query({"range": {"price.outlet": {"gte": pricerange["min"], "lte": pricerange["max"]}}})
        else:
            s = s.query({"range": {"price.retail": {"gt": 0.0}}}).query({"range": {"price.outlet": {"gt": 0.0}}})
        return s

    def select_pricerange(self, query=None, gender=None, sessionid=None, sessionname=None, brand=None,
                       kind=None) -> dict:
        s = self.__search(query=query, gender=gender, sessionid=sessionid, sessionname=sessionname, brand=brand, kind=kind)
        s = s[:1]
        s.aggs.metric("minprice", "min", field="price.outlet")
        s.aggs.metric("maxprice", "max", field="price.outlet")
        results = s.execute()

        if not results:
            raise NoContentError()
        else:
            return {
                "min": round(results.aggs.minprice.value, 2),
                "max": round(results.aggs.maxprice.value, 2)
            }

    def get_total(self, query=None, gender=None, sessionid=None, sessionname=None, brand=None, kind=None,
                    pricerange=None) -> int:
        s = self.__search(query=query, gender=gender, sessionid=sessionid, sessionname=sessionname, brand=brand, kind=kind, pricerange=pricerange)
        s = s[:0]
        results = s.execute()
        total = results.hits.total
        return total

    def select_brands(self, query=None, gender=None, sessionid=None, sessionname=None, brand=None, kind=None,
                   pricerange=None) -> List[dict]:
        s = self.__search(query=query, gender=gender, sessionid=sessionid, sessionname=sessionname, brand=brand, kind=kind, pricerange=pricerange)
        s = s[:0]
        s.aggs.bucket("brands", "terms", field="brand.keyword", size=2147483647)
        results = s.execute()
        if not results.aggs.brands.buckets:
            raise NoContentError()
        else:
            return [{"brand": hit.key, "amount": hit.doc_count} for hit in results.aggs.brands.buckets]

    def select_kinds(self, query=None, gender=None, sessionid=None, sessionname=None, brand=None, kind=None,
                   pricerange=None) -> List[dict]:
        s = self.__search(query=query, gender=gender, sessionid=sessionid, sessionname=sessionname, brand=brand, kind=kind, pricerange=pricerange)
        s = s[:0]
        s.aggs.bucket("kinds", "terms", field="kind.keyword", size=2147483647)
        results = s.execute()
        if not results.aggs.kinds.buckets:
            raise NoContentError()
        else:
            return [{"kind": hit.key, "amount": hit.doc_count} for hit in results.aggs.kinds.buckets]

    def select(self, query=None, gender=None, sessionid=None, sessionname=None, brand=None, kind=None,
                   pricerange=None, page=1, pagesize=10) -> List[Product]:
        s = self.__search(query=query, gender=gender, sessionid=sessionid, sessionname=sessionname, brand=brand, kind=kind, pricerange=pricerange)
        beginpage = (page - 1) * pagesize
        endpage = page * pagesize
        s = s[beginpage:endpage]
        results = s.execute()
        if not results:
            raise NoContentError()
        else:
            return results

    def select_by_id(self, id_) -> Product:
        s = Product.search(using=self.es)
        s = s[:1]
        s = s.filter("term", _id=id_)
        results = s.execute()
        if not results:
            raise NotFoundError()
        else:
            return results[0]

    def select_by_id_list(self, id_list) -> List[Product]:
        s = Product.search(using=self.es)
        s = s[:len(id_list)]
        s = s.filter("terms", _id=id_list)
        results = s.execute()
        if not results:
            raise NoContentError()
        else:
            return results
