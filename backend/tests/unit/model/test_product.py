from backend.model import Product
from backend.tests.factories import ProductFactory


def test_product_get(es_object):
    obj = ProductFactory.create()
    obj.save(using=es_object.connection)

    res = Product.get(using=es_object.connection, id=obj.meta["id"])

    assert res is not None
    assert type(res) is Product
    assert res.meta["id"] == obj.meta["id"]
    assert res.meta["index"] == "store"
    assert res.meta["doc_type"] == "products"


def test_product_dict(es_object):
    obj = ProductFactory.create()
    obj.save(using=es_object.connection)

    res = Product.get(using=es_object.connection, id=obj.meta["id"])
    obj_dict = res.get_dict()

    for key in ["id", "name", "link", "kind", "brand", "details", "care", "about", "images", "sessionid", "sessionname", "gender", "price"]:
        assert key in obj_dict
        assert len(obj_dict.keys()) == 13

        for pkey in ["outlet", "retail", "symbol"]:
            assert pkey in obj_dict["price"]
            assert len(obj_dict["price"].keys()) == 3


def test_product_dict_min(es_object):
    obj = ProductFactory.create()
    obj.save(using=es_object.connection)

    res = Product.get(using=es_object.connection, id=obj.meta["id"])
    obj_dict_min = res.get_dict_min()

    for key in ["id", "name", "image", "price", "discount"]:
        assert key in obj_dict_min
        assert len(obj_dict_min.keys()) == 5

        for pkey in ["outlet", "retail", "symbol"]:
            assert pkey in obj_dict_min["price"]
            assert len(obj_dict_min["price"].keys()) == 3
