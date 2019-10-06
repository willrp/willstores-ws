from typing import List

from backend.model import Session, Product
from backend.dao.es import ES
from backend.errors.no_content_error import NoContentError
from backend.errors.not_found_error import NotFoundError


class SessionService(object):
    def __init__(self):
        self.es = ES().connection

    def __count_products(self, sessionid) -> int:
        s = Product.search(using=self.es)
        s = s.filter({"term": {"sessionid.keyword": sessionid}})
        s = s[:0]
        results = s.execute()

        return results.hits.total

    def select(self, gender=None, name=None) -> List[dict]:
        s = Session.search(using=self.es)
        s = s[:10000]
        if gender is not None:
            s = s.filter("term", gender=gender.lower())
        if name is not None:
            s = s.query("match_phrase", name=name)
        results = s.execute()

        if not results:
            raise NoContentError()
        else:
            sessions = []
            for hit in results:
                sdict = hit.get_dict()
                total = self.__count_products(hit.meta["id"])
                sdict["total"] = total
                sessions.append(sdict)

            return sessions

    def select_by_id(self, id_) -> Session:
        s = Session.search(using=self.es)
        s = s[:1]
        s = s.filter("term", _id=id_)
        results = s.execute()
        try:
            return results.hits[0]
        except IndexError:
            raise NotFoundError()
