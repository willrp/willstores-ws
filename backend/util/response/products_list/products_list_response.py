from flask_restplus import fields

from ..models.product import ProductResponse
from ..models.price import PriceResponse
from .products_list_schema import ProductsListSchema


class ProductsListResponse(object):
    @staticmethod
    def get_model(api, name):
        return api.model(
            name,
            {
                "products": fields.List(fields.Nested(ProductResponse.get_model(api, "ProductOut"))),
                "total": fields.Nested(PriceResponse.get_model(api, "PriceOut"))
            }
        )

    @staticmethod
    def marshall_json(data_out):
        schema = ProductsListSchema()
        jsonsend = schema.load(data_out)
        return jsonsend
