from elasticsearch_dsl import DocType, Text, Keyword, Long


class Session(DocType):
    """
    Session model, on which Products are grouped.

        id: Session's id. Made by Elasticsearch
        name: Session's name. UPPERCASE
        gender: Session's target gender
        image: Session's image address
        pos: Session's position to be shown in the list
        storename: The store's name from which the data was crawled
    """

    gender = Text(fields={"keyword": Keyword()}, required=True)
    image = Text(fields={"keyword": Keyword()}, required=True)
    name = Text(fields={"keyword": Keyword()}, required=True)
    pos = Long(required=True)
    storename = Text(fields={"keyword": Keyword()}, required=True)

    class Meta:
        index = "store"
        doc_type = "sessions"

    def get_dict(self) -> dict:
        return {
            "id": self.meta["id"],
            "name": self.name,
            "gender": self.gender,
            "image": self.image
        }
