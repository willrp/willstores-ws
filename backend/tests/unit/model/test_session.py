from backend.model import Session
from backend.tests.factories import SessionFactory


def test_session_get(es_object):
    obj = SessionFactory.create()
    obj.save(using=es_object.connection)

    res = Session.get(using=es_object.connection, id=obj.meta["id"])

    assert res is not None
    assert type(res) is Session
    assert res.meta["id"] == obj.meta["id"]
    assert res.meta["index"] == "store"
    assert res.meta["doc_type"] == "sessions"


def test_session_dict(es_object):
    obj = SessionFactory.create()
    obj.save(using=es_object.connection)

    res = Session.get(using=es_object.connection, id=obj.meta["id"])
    obj_dict = res.get_dict()

    for key in ["id", "name", "gender", "image"]:
        assert key in obj_dict

    assert len(obj_dict.keys()) == 4
