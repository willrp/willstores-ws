from factory import Factory, Sequence, Faker
from factory.fuzzy import FuzzyChoice

from backend.model import Session


class SessionFactory(Factory):
    gender = FuzzyChoice(["Men", "Women"])
    image = Faker("image_url")
    name = Sequence(lambda n: "Session Name %s" % n)
    pos = Sequence(lambda n: n)
    storename = "WillBuyer"

    class Meta:
        model = Session
