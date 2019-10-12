from factory import Factory, Sequence, List, build, Faker
from factory.fuzzy import FuzzyChoice, FuzzyDecimal

from ...model import Price, Product


class PriceFactory(Factory):
    outlet = FuzzyDecimal(50.0, 100.0, 2)
    retail = FuzzyDecimal(150.0, 200.0, 2)

    class Meta:
        model = Price


class ProductFactory(Factory):
    about = Faker("text")
    brand = Sequence(lambda n: "Brand %s" % n)
    care = Faker("text")
    code = Faker("msisdn")
    details = List([Faker("text"), Faker("text")])
    gender = FuzzyChoice(["Men", "Women"])
    images = List([Faker("image_url"), Faker("image_url")])
    kind = Sequence(lambda n: "Kind %s" % n)
    link = Faker("text")
    name = Sequence(lambda n: "Product Name %s" % n)
    price = build(dict, FACTORY_CLASS=PriceFactory)
    sessionid = Sequence(lambda n: "Session ID %s" % n)
    sessionname = Sequence(lambda n: "Session Name %s" % n)
    storename = "WillBuyer"

    class Meta:
        model = Product
