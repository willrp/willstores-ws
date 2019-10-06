from elasticsearch_dsl import DocType, Text, Keyword, Object, Float

from .price import Price


class Product(DocType):
    """
    Product model, sold at the store:
        id: Product's id. Made by Elasticsearch
        name: Product's name
        link: Link that directly points to the Product
        type: Product's type, e. g., Dress
        brand: Product's brand, e. g., London Rebel
        code: Product's shop code
        details: List containing Product's details
        care: String that represents how to preserve the Product
        about: Information about the Product
        images: List of Product's images addresses
        sessionid: Id of the Session that the Product was crawled from.
        sessionname: Name of the Session that the Product was crawled from.
        gender: Product's target gender
        price: Product's price. Composition with class Price
        storename: The store's name from which the data was crawled
    """

    about = Text(fields={"keyword": Keyword()}, required=True)
    brand = Text(fields={"keyword": Keyword()}, required=True)
    care = Text(fields={"keyword": Keyword()}, required=True)
    code = Text(fields={"keyword": Keyword()}, required=True)
    details = Text(fields={"keyword": Keyword()}, multi=True, required=True)
    gender = Text(fields={"keyword": Keyword()}, required=True)
    images = Text(fields={"keyword": Keyword()}, multi=True, required=True)
    kind = Text(fields={"keyword": Keyword()}, required=True)
    link = Text(fields={"keyword": Keyword()}, required=True)
    name = Text(fields={"keyword": Keyword()}, required=True)
    price = Object(
        doc_class=Price,
        multi=False,
        required=True,
        properties={
            "outlet": Float(required=True),
            "retail": Float(required=True)
        }
    )
    sessionid = Text(fields={"keyword": Keyword()}, required=True)
    sessionname = Text(fields={"keyword": Keyword()}, required=True)
    storename = Text(fields={"keyword": Keyword()}, required=True)

    class Meta:
        index = "store"
        type = "products"
        doc_type = "products"

    def __get_main_image(self) -> str:
        return self.images[0]

    def get_dict(self) -> dict:
        return {
            "id": self.meta["id"],
            "name": self.name,
            "link": self.link,
            "kind": self.kind,
            "brand": self.brand,
            "details": list(self.details),
            "care": self.care,
            "about": self.about,
            "images": list(self.images),
            "sessionid": self.sessionid,
            "sessionname": self.sessionname,
            "gender": self.gender,
            "price": self.price.get_dict()
        }

    def get_dict_min(self) -> dict:
        return {
            "id": self.meta["id"],
            "name": self.name,
            "image": self.__get_main_image(),
            "price": self.price.get_dict(),
            "discount": self.price.discount
        }
